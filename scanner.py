import pymem
import pymem.process
import ctypes
from ctypes import wintypes
import struct
import json
import os

# Windows API constants
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]

class MegaBonkScanner:
    def __init__(self, process_name="MegaBonk.exe", progress_callback=None, log_callback=None):
        self.pm = pymem.Pymem(process_name)
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.pointer_cache = {}
        self.config_file = "shop_scanner_config.json"
        self.learned_regions = self.load_learned_regions()
        
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
    
    def update_progress(self, value, maximum=100):
        if self.progress_callback:
            self.progress_callback(value, maximum)
    
    def load_learned_regions(self):
        """Load previously learned shop regions"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_learned_regions(self, regions):
        """Save learned regions for future scans"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(regions, f)
            self.log(f"💾 Saved {len(regions)} region(s) for fast scanning")
        except:
            pass
    
    def read_pointer(self, address):
        if address in self.pointer_cache:
            return self.pointer_cache[address]
        try:
            val = self.pm.read_longlong(address)
            self.pointer_cache[address] = val
            return val
        except:
            return 0
    
    def read_int(self, address):
        try:
            return self.pm.read_int(address)
        except:
            return None
    
    def read_bool(self, address):
        try:
            value = self.pm.read_bytes(address, 1)[0]
            return value in [0, 1], value
        except:
            return False, None
    
    def read_string_unity(self, address):
        try:
            if address == 0 or address is None:
                return None
            length = self.read_int(address + 0x10)
            if length is None or length <= 0 or length > 500:
                return None
            string_data = self.pm.read_bytes(address + 0x14, length * 2)
            return string_data.decode('utf-16-le', errors='ignore')
        except:
            return None
    
    def read_list_data(self, list_pointer):
        try:
            if list_pointer == 0:
                return 0, 0
            items_array = self.read_pointer(list_pointer + 0x10)
            count = self.read_int(list_pointer + 0x18)
            if count is None:
                count = 0
            return items_array, count
        except:
            return 0, 0
    
    def is_valid_pointer(self, ptr):
        return 0x10000 < ptr < 0x7FFFFFFFFFFF
    
    def quick_validate(self, data, offset):
        """Fast validation without memory reads"""
        try:
            # Check rarity (offset 0x90)
            rarity_offset = offset + 0x90
            if rarity_offset + 4 > len(data):
                return False
            rarity = struct.unpack('<i', data[rarity_offset:rarity_offset+4])[0]
            if not (0 <= rarity <= 3):
                return False
            
            # Check pointers (0x98, 0xA0, 0xA8)
            for ptr_offset in [0x98, 0xA0, 0xA8]:
                check_offset = offset + ptr_offset
                if check_offset + 8 > len(data):
                    return False
                ptr = struct.unpack('<Q', data[check_offset:check_offset+8])[0]
                if not self.is_valid_pointer(ptr):
                    return False
            
            # Check done boolean (0xB8)
            done_offset = offset + 0xB8
            if done_offset >= len(data):
                return False
            if data[done_offset] not in [0, 1]:
                return False
            
            return True
        except:
            return False
    
    def validate_shop_structure(self, address):
        try:
            rarity = self.read_int(address + 0x90)
            if rarity is None or not (0 <= rarity <= 3):
                return False
            
            items_ptr = self.read_pointer(address + 0x98)
            if not self.is_valid_pointer(items_ptr):
                return False
            
            prices_ptr = self.read_pointer(address + 0xA0)
            if not self.is_valid_pointer(prices_ptr):
                return False
            
            is_bool, _ = self.read_bool(address + 0xB8)
            if not is_bool:
                return False
            
            items_array, items_count = self.read_list_data(items_ptr)
            prices_array, prices_count = self.read_list_data(prices_ptr)
            
            if items_count != 3 or prices_count != 3:
                return False
            
            if not self.is_valid_pointer(items_array) or not self.is_valid_pointer(prices_array):
                return False
            
            return True
        except:
            return False
    
    def scan_single_region(self, region_base, region_size, shop_found_callback=None):
        """Scan a single memory region for shops"""
        shops = []
        found_addresses = set()
        
        try:
            data = self.pm.read_bytes(region_base, region_size)
            
            # Scan every 8 bytes
            for offset in range(0, len(data) - 0xC0, 8):
                if self.quick_validate(data, offset):
                    addr = region_base + offset
                    
                    if addr not in found_addresses:
                        if self.validate_shop_structure(addr):
                            found_addresses.add(addr)
                            shops.append(addr)
                            self.log(f"✅ Shop #{len(shops)} at 0x{addr:X}")
                            
                            if shop_found_callback:
                                shop_data = self.get_shop_data(addr)
                                if shop_data:
                                    shop_found_callback(shop_data)
        except:
            pass
        
        return shops
    
    def find_shop_regions(self):
        """Find all memory regions that could contain shops"""
        base_address = 0
        mbi = MEMORY_BASIC_INFORMATION()
        kernel32 = ctypes.windll.kernel32
        
        regions = []
        
        while base_address < 0x7FFFFFFFFFFF:
            result = kernel32.VirtualQueryEx(
                self.pm.process_handle,
                ctypes.c_void_p(base_address),
                ctypes.byref(mbi),
                ctypes.sizeof(mbi)
            )
            
            if result == 0:
                break
            
            if mbi.BaseAddress is None or mbi.RegionSize is None:
                base_address += 0x1000
                continue
            
            if (mbi.State == MEM_COMMIT and 
                mbi.Type == 0x20000 and
                mbi.Protect in [PAGE_READWRITE, PAGE_EXECUTE_READWRITE] and
                0x10000 < mbi.RegionSize < 0x2000000):
                
                regions.append({
                    'base': mbi.BaseAddress,
                    'size': mbi.RegionSize
                })
            
            base_address = mbi.BaseAddress + mbi.RegionSize
        
        return regions
    
    def find_all_shops(self, shop_found_callback=None, use_learned=True):
        """Find all shops - uses learned regions if available"""
        self.log("🔍 Starting scan...")
        self.pointer_cache.clear()
        
        shops = []
        found_addresses = set()
        regions_with_shops = []
        
        try:
            # FAST PATH: Try learned regions first
            if use_learned and self.learned_regions:
                self.log(f"⚡ Using {len(self.learned_regions)} saved region(s)")
                
                shops_found = False
                for idx, region_info in enumerate(self.learned_regions):
                    try:
                        # Verify region still exists
                        test_read = self.pm.read_bytes(region_info['base'], 8)
                        
                        region_shops = self.scan_single_region(
                            region_info['base'], 
                            region_info['size'],
                            shop_found_callback
                        )
                        
                        if region_shops:
                            shops.extend(region_shops)
                            found_addresses.update(region_shops)
                            shops_found = True
                        
                        self.update_progress(idx + 1, len(self.learned_regions))
                    except Exception as e:
                        self.log(f"⚠️ Saved region 0x{region_info['base']:X} invalid: {e}")
                
                if shops_found and shops:
                    self.log(f"✅ Found {len(shops)} shop(s) in saved regions!")
                    return shops
                else:
                    self.log("⚠️ No shops in saved regions, doing full scan...")
            
            # FULL SCAN: Search all regions
            all_regions = self.find_shop_regions()
            self.log(f"📊 Scanning {len(all_regions)} memory regions...")
            self.update_progress(0, len(all_regions))
            
            for idx, region in enumerate(all_regions):
                region_shops = self.scan_single_region(
                    region['base'], 
                    region['size'],
                    shop_found_callback
                )
                
                if region_shops:
                    shops.extend(region_shops)
                    found_addresses.update(region_shops)
                    
                    # Remember this region
                    regions_with_shops.append({
                        'base': region['base'],
                        'size': region['size']
                    })
                    
                    self.log(f"🎯 Found {len(region_shops)} shop(s) in region 0x{region['base']:X}")
                
                self.update_progress(idx + 1, len(all_regions))
            
            # Save regions that had shops
            if regions_with_shops:
                self.save_learned_regions(regions_with_shops)
                self.learned_regions = regions_with_shops
            
            self.log(f"✅ Scan complete! Found {len(shops)} shop(s)")
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
        
        return shops
    
    def read_item_data(self, item_pointer):
        if item_pointer == 0:
            return None
        
        try:
            in_item_pool = self.read_bool(item_pointer + 0x50)[1]
            eitem_ptr = self.read_pointer(item_pointer + 0x54)
            description_ptr = self.read_pointer(item_pointer + 0x58)
            short_desc_ptr = self.read_pointer(item_pointer + 0x60)
            rarity = self.read_int(item_pointer + 0x70)
            max_amount = self.read_int(item_pointer + 0x80)
            
            description = self.read_string_unity(description_ptr)
            short_description = self.read_string_unity(short_desc_ptr)
            
            item_name = None
            if eitem_ptr != 0:
                item_name = self.read_string_unity(eitem_ptr)
            
            display_desc = short_description if short_description else description
            if not display_desc:
                display_desc = 'No description'
            
            return {
                'name': item_name if item_name else 'Unknown Item',
                'description': display_desc,
                'rarity': rarity,
                'max_amount': max_amount,
                'in_pool': in_item_pool
            }
        except:
            return None
    
    def get_shop_data(self, shop_address):
        items_list_ptr = self.read_pointer(shop_address + 0x98)
        prices_list_ptr = self.read_pointer(shop_address + 0xA0)
        
        if items_list_ptr == 0:
            return None
        
        items_array_ptr, item_count = self.read_list_data(items_list_ptr)
        
        if items_array_ptr == 0 or item_count == 0:
            return None
        
        prices = []
        if prices_list_ptr != 0:
            prices_array_ptr, prices_count = self.read_list_data(prices_list_ptr)
            if prices_array_ptr != 0:
                for i in range(min(prices_count, item_count)):
                    price = self.read_int(prices_array_ptr + 0x20 + (i * 4))
                    prices.append(price if price is not None else 0)
        
        array_start = items_array_ptr + 0x20
        items = []
        
        for i in range(item_count):
            item_ptr = self.read_pointer(array_start + (i * 8))
            if item_ptr == 0:
                return None
            
            item_data = self.read_item_data(item_ptr)
            if not item_data:
                return None
            
            items.append(item_data)
        
        done = self.read_bool(shop_address + 0xB8)[1]
        rarity = self.read_int(shop_address + 0x90)
        
        return {
            'address': shop_address,
            'rarity': rarity,
            'done': done,
            'items': items,
            'prices': prices
        }