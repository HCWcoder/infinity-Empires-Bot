#!/usr/bin/env python3
"""
City Manager - Handles city navigation and periodic actions
"""

import time
import json
import os
from typing import Optional, Tuple, List


class CityManager:
    """Manages city navigation and periodic actions"""
    
    def __init__(self, bot):
        """Initialize with a bot instance"""
        self.bot = bot
        self.config = self.load_config()
        self.last_reset = 0  # Track when we last reset position
    
    def _load_ruin_coordinates(self):
        """Load all ruin coordinates organized by level and area"""
        return {
            "Level 1": {
                "Area 1 (Founding of the Three Kingdoms)": [
                    (15,149), (33,175), (34,110), (73,58), (119,50), (130,85), (133,133), (140,88), 
                    (157,131), (156,90), (172,111), (180,59), (193,26), (193,45), (200,151), (211,43), 
                    (214,34), (226,36), (238,72), (243,39), (246,30), (266,90), (270,57), (289,128), 
                    (310,120), (314,60), (350,55)
                ],
                "Area 2 (Discovering Relics)": [
                    (57,214), (68,211), (94,206), (111,221), (136,224), (144,180), (152,222), (158,198), 
                    (206,170), (29,361), (62,315), (67,359), (78,263), (92,255), (101,332), (124,318), 
                    (133,350), (155,282), (9,480), (17,495), (19,455), (27,464), (48,491), (63,405), 
                    (108,422), (115,392), (123,377)
                ],
                "Area 3 (War in the Three Kingdoms)": [
                    (49,575), (52,557), (64,532), (71,559), (81,620), (96,566), (114,574), (132,583), 
                    (138,593), (17,746), (18,710), (21,721), (32,637), (36,710), (37,726), (53,727), 
                    (55,639), (71,711), (46,777), (54,819), (63,800), (67,753), (84,736), (84,826), 
                    (100,790), (102,798), (126,805)
                ],
                "Area 4 (The Gnome Invasion)": [
                    (76,840), (143,880), (152,833), (152,853), (152,860), (153,921), (164,893), (172,834), 
                    (194,834), (191,895), (205,937), (221,873), (265,862), (275,890), (279,865), (298,957), 
                    (306,908), (314,932)
                ],
                "Area 5 (A New Summons)": [
                    (449,961), (455,981), (467,966), (472,985), (487,934), (508,902), (525,923), (544,931), 
                    (565,950), (581,932), (585,965), (596,975)
                ],
                "Area 6 (History of the Magic Academy)": [
                    (639,950), (665,883), (670,856), (680,961), (681,858), (691,875), (708,900), (712,878), 
                    (724,892), (727,912), (729,947), (739,942)
                ],
                "Area 7 (The Dragons and the Treasury)": [
                    (800,871), (842,865), (843,925), (866,907), (868,900), (891,874), (894,901), (904,842), 
                    (910,855), (843,770), (843,805), (851,813), (888,761), (892,791), (892,821), (912,762), 
                    (913,778), (916,753)
                ],
                "Area 8 (Sea Trade)": [
                    (960,922), (972,905), (976,925), (977,870), (996,869), (1011,868), (1012,910), (1016,846), 
                    (1021,884), (1059,886), (1091,879), (1094,900), (1095,891), (1104,835), (1115,907), 
                    (1137,854), (1149,844), (1159,833), (1032,936), (1037,926), (1062,948), (1072,940), 
                    (1077,932), (1104,977), (1113,924), (1123,966), (1133,948)
                ],
                "Area 9 (The Call of the Three Kingdoms)": [
                    (972,791), (990,821), (1013,754), (1022,823), (1023,746), (1033,850), (1036,778), 
                    (1036,817), (1046,778), (1103,782), (1116,730), (1138,782), (1139,717), (1143,775), 
                    (1155,786), (1164,781), (1179,755), (1180,765)
                ],
                "Area 10 (The Doomsday Prophecy)": [
                    (1052,715), (1063,636), (1067,726), (1073,697), (1075,688), (1119,670), (1121,624), 
                    (1139,629), (1139,664), (1012,574), (1016,585), (1020,608), (1038,555), (1039,593), 
                    (1041,562), (1058,575), (1067,573), (1096,599)
                ],
                "Area 11 (Harold's Ice Wall)": [
                    (1073,438), (1102,417), (1103,475), (1105,496), (1116,449), (1122,487), (1134,535), 
                    (1138,547), (1144,415), (1043,348), (1053,343), (1070,383), (1072,346), (1079,303), 
                    (1102,377), (1110,397), (1152,402), (1153,414)
                ],
                "Area 12 (The Royal Alchemist Academy)": [
                    (1008,261), (1031,239), (1040,199), (1041,220), (1042,287), (1052,206), (1065,217), 
                    (1075,238), (1079,278), (1055,197), (1093,148), (1101,244), (1107,142), (1118,216), 
                    (1120,185), (1129,151), (1149,221), (1156,168)
                ],
                "Area 13 (Sovereign Tomb)": [
                    (943,228), (944,175), (961,149), (968,174), (984,147), (1008,128), (1020,199), 
                    (1039,137), (1053,136), (1023,70), (1024,43), (1037,98), (1045,76), (1073,114), 
                    (1112,98), (1134,70), (1152,68), (1169,113)
                ],
                "Area 14 (Hornheim's Disappearance)": [
                    (732,123), (737,87), (753,141), (769,84), (773,163), (787,226), (797,202), (801,123), 
                    (811,123), (848,124), (853,92), (853,105), (885,93), (901,115), (919,62), (954,113), 
                    (986,123), (1007,101)
                ],
                "Area 15 (The Empire Crumbles)": [
                    (361,82), (375,141), (378,56), (389,108), (394,140), (400,182), (426,68), (449,93), 
                    (451,131), (468,72), (487,87), (497,63), (501,99), (505,65), (514,144), (517,113), 
                    (526,172), (554,107), (568,160), (579,142), (595,73), (601,96), (608,74), (629,93), 
                    (647,182), (673,115), (710,87)
                ]
            },
            "Level 2": {
                "Area 16 (Sage Council)": [
                    (145,260), (155,267), (167,286), (170,329), (177,278), (224,222), (239,222), (243,232), 
                    (255,262), (242,199), (257,231), (269,231), (283,203), (306,165), (309,192), (338,129), 
                    (365,160), (368,141)
                ],
                "Area 17 (Enigma Lieu)": [
                    (140,392), (144,459), (151,353), (154,367), (164,447), (165,405), (180,425), (184,378), 
                    (190,412), (211,369), (214,430), (235,353)
                ],
                "Area 18 (Well of Time)": [
                    (151,468), (155,483), (192,558), (193,520), (208,442), (210,542), (229,537), (233,509), 
                    (246,549), (264,557), (280,514), (300,536)
                ],
                "Area 19 (The First Gnome Invasion)": [
                    (129,726), (149,700), (172,723), (184,690), (190,664), (198,687), (211,708), (212,642), 
                    (218,705), (244,655), (258,654), (266,683), (117,642), (125,631), (127,653), (161,614), 
                    (167,641), (177,570), (178,613), (195,617), (203,644), (204,606), (247,606), (261,645)
                ],
                "Area 20 (Above and Below)": [
                    (226,840), (258,809), (270,801), (273,844), (284,828), (295,767), (308,760), (321,751), 
                    (341,770), (149,763), (174,755), (179,783), (224,781), (238,707), (241,773), (278,704), 
                    (282,691), (298,738)
                ],
                "Area 21 (Summoning Ban)": [
                    (483,835), (494,859), (516,809), (517,754), (523,809), (535,806), (543,782), (556,789), 
                    (571,809), (352,860), (363,884), (374,894), (386,844), (386,871), (403,926), (418,928), 
                    (419,845), (423,916)
                ],
                "Area 22 (World Heart)": [
                    (642,846), (646,858), (657,841), (663,765), (673,766), (686,835), (690,853), (698,740), 
                    (726,847), (553,893), (557,868), (572,854), (574,894), (590,899), (591,892), (596,938), 
                    (604,900), (609,911)
                ],
                "Area 23 (Terrifying Rumors)": [
                    (835,665), (836,692), (840,681), (856,674), (856,684), (875,694), (880,728), (889,684), 
                    (890,668), (717,801), (718,750), (738,804), (740,812), (772,776), (784,778), (788,816), 
                    (814,815), (820,807)
                ],
                "Area 24 (Founding of the Empire)": [
                    (885,605), (915,620), (915,653), (918,667), (925,666), (927,644), (943,661), (945,599), 
                    (947,653), (948,588), (965,606), (975,656), (926,764), (929,705), (930,777), (933,743), 
                    (956,787), (958,726), (967,697), (975,762), (980,751), (978,688), (1006,667), (1022,671)
                ],
                "Area 25 (Five Great Kingdoms)": [
                    (899,367), (933,323), (936,399), (955,385), (958,475), (959,416), (974,394), (1011,368), 
                    (1016,347), (977,447), (989,435), (1003,404), (1016,481), (1024,388), (1036,470), 
                    (1041,440), (1047,410), (1085,398)
                ],
                "Area 26 (The Gnome's Birth and Exile)": [
                    (877,254), (888,260), (910,256), (922,267), (927,292), (932,285), (933,304), (936,316), 
                    (952,280), (953,243), (958,264), (960,328), (978,298), (982,321), (991,287)
                ],
                "Area 27 (The War of Five Kingdoms)": [
                    (752,234), (754,200), (758,213), (763,301), (787,306), (792,343), (799,293), (804,314), 
                    (836,283), (816,200), (820,211), (833,224), (880,220), (899,188), (908,154), (911,229), 
                    (914,194), (931,188)
                ],
                "Area 28 (The Alchemists)": [
                    (367,186), (414,209), (420,267), (426,191), (428,247), (453,204), (467,249), (493,222), 
                    (501,228), (518,253), (538,241), (539,251), (546,188), (554,217), (558,266), (572,233), 
                    (600,192), (624,199), (646,226), (669,224), (695,183), (696,192), (697,158), (706,152), 
                    (706,216), (722,214), (734,172)
                ],
                "Area 29 (Hornheim)": [
                    (337,282), (341,210), (358,224), (358,235), (360,246), (362,196), (364,276), (369,251), 
                    (383,307), (386,234), (406,283), (415,291)
                ]
            },
            "Level 3": {
                "Area 30 (Stela of New World)": [
                    (268,379), (285,252), (289,361), (299,330), (301,263), (309,257), (310,275), (315,315), 
                    (356,332), (260,397), (276,411), (287,419), (295,453), (314,454), (326,423), (335,383), 
                    (338,402), (397,420)
                ],
                "Area 31 (Temple of Norheim)": [
                    (269,666), (279,581), (296,678), (332,570), (333,556), (343,615), (376,589), (386,547), 
                    (395,567), (336,710), (344,751), (356,656), (357,756), (367,712), (373,668), (381,741), 
                    (386,624), (406,636)
                ],
                "Area 32 (History of the Tribes)": [
                    (362,821), (384,808), (401,821), (421,812), (426,758), (457,815), (466,752), (477,775), 
                    (490,742), (437,658), (494,652), (504,694), (508,644), (518,666), (522,699), (535,688), 
                    (539,673), (543,682), (526,745), (539,748), (565,756), (569,708), (591,728), (600,730), 
                    (612,708), (624,759), (626,774)
                ],
                "Area 33 (Forbidden Zone)": [
                    (739,677), (740,707), (747,748), (774,643), (775,740), (777,692), (790,690), (800,657), 
                    (812,688), (801,621), (808,650), (809,664), (818,593), (825,648), (830,615), (837,622), 
                    (837,632), (878,604)
                ],
                "Area 34 (Creation and the Guardians)": [
                    (925,497), (932,554), (935,500), (942,571), (950,534), (960,493), (984,510), (989,547), 
                    (991,554), (998,538), (1014,504), (1039,507)
                ],
                "Area 35 (The Energy Circle)": [
                    (801,548), (806,558), (859,515), (868,523), (868,533), (893,564), (897,511), (903,492), 
                    (907,483), (804,390), (822,399), (842,400), (853,413), (861,363), (862,329), (876,356), 
                    (886,375), (900,331)
                ],
                "Area 36 (The Destruction of Civilization)": [
                    (661,276), (675,271), (691,253), (693,272), (705,328), (708,311), (721,292), (727,264), 
                    (727,314), (729,294), (738,265), (738,333)
                ],
                "Area 37 (The Memory Modification)": [
                    (463,325), (471,291), (486,287), (498,343), (501,329), (511,286), (517,358), (538,337), 
                    (544,310), (545,345), (563,357), (576,352)
                ]
            }
        }
    
    def load_config(self) -> dict:
        """Load UI elements configuration"""
        try:
            with open("minimal_config.json", "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def log(self, message: str):
        """Log message with timestamp"""
        timestamp = time.strftime("[%H:%M:%S]")
        print(f"{timestamp} [CityManager] {message}")
    
    def is_in_city(self) -> bool:
        """Check if we're in the city by looking for map button"""
        if not self.bot.device:
            return False
            
        map_button_config = self.config.get("ui_elements", {}).get("map_button")
        if not map_button_config:
            self.log("Map button config not found")
            return False
            
        found, _ = self.bot.detect_ui_element_in_area(
            map_button_config["image_path"], 
            map_button_config.get("search_area"),
            map_button_config.get("threshold", 0.6)
        )
        
        return found
    
    def reset_to_city(self) -> bool:
        """Reset position to city center (map -> home button)"""
        self.log("Resetting position to city center...")
        
        # Step 1: Click map button
        if not self.click_element("map_button"):
            self.log("Failed to click map button")
            return False
            
        # Wait for map to load
        time.sleep(5)
        
        # Step 2: Click home button
        if not self.click_element("home_button"):
            self.log("Failed to click home button")
            return False
            
        # Wait for city to load
        time.sleep(6)
        
        # Verify we're in city
        if self.is_in_city():
            self.log("✓ Successfully reset to city")
            self.last_reset = time.time()
            return True
        else:
            self.log("✗ Failed to verify city position after reset")
            return False

    def click_element(self, element_name: str, max_attempts: int = 4, threshold: float = 0.5) -> bool:
        """Click a UI element by name with retry logic"""
        if not self.bot.device:
            self.log("No device connected")
            return False
            
        element_config = self.config.get("ui_elements", {}).get(element_name)
        if not element_config:
            self.log(f"Element '{element_name}' not found in config")
            return False
        
        for attempt in range(max_attempts):
            found, result = self.bot.detect_ui_element_in_area(
                element_config["image_path"],
                element_config.get("search_area"),
                element_config.get("threshold", threshold)
            )
            
            if found:
                # result is already center coordinates (center_x, center_y)
                center_x, center_y = result
                
                # Adjust X coordinate by adding 15 for clicking
                if element_name in ["coordX", "coordY"]:
                    adjusted_x = center_x + 45
                    self.log(f"Adjusting click X coordinate for {element_name}: {center_x} -> {adjusted_x}")
                else:
                    adjusted_x = center_x
                
                if self.bot.click_coordinate(adjusted_x, center_y):
                    self.log(f"✓ Clicked {element_name} at ({adjusted_x}, {center_y})")
                    return True
                else:
                    self.log(f"✗ Failed to click {element_name}")
                    return False
            else:
                if attempt < max_attempts - 1:
                    self.log(f"Element '{element_name}' not found, attempt {attempt + 1}/{max_attempts}")
                    
        self.log(f"✗ Element '{element_name}' not found after {max_attempts} attempts")
        return False
    
    def ensure_in_city(self) -> bool:
        """Ensure we're in the city, reset if needed"""
        if self.is_in_city():
            return True
        
        self.log("Not in city, attempting to reset position...")
        return self.reset_to_city()
    
    def go_to_research_area(self) -> bool:
        """Navigate to research area: reset -> castle -> research area"""
        self.log("Going to research area...")
        
        # Ensure we're in city
        if not self.ensure_in_city():
            return False
            
        # Click castle
        if not self.click_element("Castle"):
            self.reset_to_city()
            return False
        time.sleep(1)
        
        if not self.click_element("Castle"):
            return False
        time.sleep(2)

        # Click research area
        if not self.click_element("ResearchArea"):
            return False
            
        self.log("✓ Successfully navigated to research area")
        return True
    
    def go_to_dragon_panel(self) -> bool:
        """Navigate to dragon panel: reset -> castle -> dragon panel"""
        self.log("Going to dragon panel...")
        
        # Ensure we're in city
        if not self.ensure_in_city():
            return False
            
        # Reset position first
        if not self.reset_to_city():
            return False
            
        # Click castle
        if not self.click_element("Castle"):
            return False
        time.sleep(1)
        
        # Click dragon panel
        if not self.click_element("DragonPanel"):
            return False
            
        self.log("✓ Successfully navigated to dragon panel")
        return True
    
    def go_to_shipment_collect(self) -> bool:
        """Navigate to shipment collect: reset -> gold pickup -> dwelling -> warehouse -> shipment"""
        self.log("Going to shipment collect...")
        
        # Ensure we're in city
        if not self.ensure_in_city():
            return False
            
        # Reset position first
        if not self.reset_to_city():
            return False
            
        # Step 1: Check for gold pickup and click if found
        if self.click_element("GoldPickup"):
            self.log("✓ Clicked gold pickup")
            time.sleep(1)
        else:
            self.log("Gold pickup not found, continuing...")
        
        # Step 2: Click dwelling area
        if not self.click_element("DwelingArea"):
            self.log("Failed to find dwelling area")
            return False
        time.sleep(1)
        
        # Step 3: Click warehouse
        if not self.click_element("WareHouse"):
            self.log("Failed to find warehouse")
            return False
        time.sleep(1)
        
        # Step 4: Check for shipment collect
        if self.click_element("ShipmentCollect"):
            self.log("✓ Found and clicked shipment collect")
            time.sleep(1)
            
            # Step 5: Try to claim shipment
            if self.click_element("ShipmentClaim"):
                self.log("✓ Clicked shipment claim")
                time.sleep(1)
                
                # Step 6: Try to continue shipment
                if self.click_element("ShipmentContinue"):
                    self.log("✓ Clicked shipment continue")
                    time.sleep(1)
            
            # Step 7: Go back
            if self.click_element("BackButton"):
                self.log("✓ Clicked back button")
                time.sleep(1)
                
            self.log("✓ Successfully completed shipment collect routine")
            return True
        else:
            self.log("No shipment collect available")
            # Still go back
            if self.click_element("BackButton"):
                self.log("✓ Clicked back button")
            return False
    
    def click_buildings_panel(self) -> bool:
        """Click buildings panel (available anytime in city)"""
        self.log("Clicking buildings panel...")
        
        if not self.ensure_in_city():
            return False
            
        return self.click_element("BuildingsPanel")
    
    def click_troops_panel(self) -> bool:
        """Click troops panel (available anytime in city)"""
        self.log("Clicking troops panel...")
        
        if not self.ensure_in_city():
            return False
            
        return self.click_element("TroopsPanel")
    
    def click_march_panel(self) -> bool:
        """Click march panel (available anytime in city)"""
        self.log("Clicking march panel...")
        
        if not self.ensure_in_city():
            return False
            
        return self.click_element("MarchPanel")
    
    def run_periodic_tasks(self) -> None:
        """Run periodic city tasks"""
        self.log("Starting periodic city tasks...")
        
        tasks = [
            ("Shipment Collection", self.go_to_shipment_collect),
            ("Research Area Check", self.go_to_research_area),
            ("Dragon Panel Check", self.go_to_dragon_panel),
        ]
        
        for task_name, task_func in tasks:
            try:
                self.log(f"Executing: {task_name}")
                result = task_func()
                if result:
                    self.log(f"✓ {task_name} completed successfully")
                else:
                    self.log(f"✗ {task_name} failed")
                
                # Wait between tasks
                time.sleep(2)
                
            except Exception as e:
                self.log(f"✗ Error in {task_name}: {e}")
                continue
        
        self.log("Periodic tasks completed")
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions"""
        return [
            "go_to_research_area",
            "go_to_dragon_panel", 
            "go_to_shipment_collect",
            "click_buildings_panel",
            "click_troops_panel",
            "click_march_panel",
            "reset_to_city",
            "explore_ruins_flow",
            "run_periodic_tasks",
            "count_available_marches"
        ]
    
    def save_explored_ruins(self, explored_ruins):
        """Save explored ruins to a file to avoid repeating them"""
        try:
            with open("explored_ruins.json", "w") as f:
                json.dump(explored_ruins, f, indent=2)
        except Exception as e:
            self.log(f"Error saving explored ruins: {e}")
    
    def load_explored_ruins(self):
        """Load previously explored ruins"""
        try:
            if os.path.exists("explored_ruins.json"):
                with open("explored_ruins.json", "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.log(f"Error loading explored ruins: {e}")
            return []
    
    def input_coordinate(self, coord_type, value):
        """Input coordinate value (X or Y)"""
        element_name = f"coord{coord_type}"  # coordX or coordY
        

        adjusted_value = value
        
        # tap this location 811, 41 dont use click element
        if(coord_type == "X"):
            self.bot.device.shell("input tap 835 41")
        elif(coord_type == "Y"):
            self.bot.device.shell("input tap 965 41")
        time.sleep(0.5)
        
        # Clear the field and input the value
        try:
            for _ in range(4):
                self.bot.device.shell("input keyevent KEYCODE_DEL")
                time.sleep(0.05)
            
            self.bot.device.shell(f"input text {adjusted_value}")
            time.sleep(0.25)
            self.bot.device.shell("input keyevent KEYCODE_ENTER")
            time.sleep(0.25)
            self.log(f"✓ Entered {coord_type}: {adjusted_value}")
            return True
            
        except Exception as e:
            self.log(f"✗ Error inputting {coord_type} coordinate: {e}")
            return False
    
    def search_ruin_at_coordinate(self, x, y):
        """Search for a ruin at specific coordinates"""
        self.log(f"Searching for ruin at ({x}, {y})")
        
        # Input X coordinate
        if not self.input_coordinate("X", str(x)):
            return False
        
        # Input Y coordinate  
        if not self.input_coordinate("Y", str(y)):
            return False
        
        self.bot.device.shell("input tap 1061 41")
        
        time.sleep(1.25)  # Wait for map to navigate
        
        self.bot.device.shell("input tap 951 313")
        time.sleep(0.25)  # Wait for map to navigate
        
        if self.click_element("exploreNew", max_attempts=1, threshold=0.4):
                self.log("✓ Successfully started exploration!")
                time.sleep(0.5)
                return True
        else:
            self.log("✗ Explore button not found")
            return False
        # Check if we found a ruin - try multiple variants
        ruin_variants = ["foundRuin6", "foundRuin4", "foundRuin5", "foundRuin3", "1231d12d"]
        ruin_found = False
        
        for ruin_variant in ruin_variants:
            if self.click_element(ruin_variant, max_attempts=2, threshold=0.43):
                self.log(f"✓ Found ruin ({ruin_variant})! Attempting to explore...")
                ruin_found = True
                break
        
        if ruin_found:
            time.sleep(0.35)
            
            # Click explore button
            if self.click_element("exploreNew", max_attempts=1, threshold=0.4):
                self.log("✓ Successfully started exploration!")
                time.sleep(0.5)
                return True
            else:
                self.log("✗ Explore button not found")
                return False
        else:
            self.log("No ruin found at this coordinate")
            return False
    
    def count_available_marches(self):
        """Count how many marches are available by checking for March1 and March2"""
        if not self.bot.device:
            self.log("No device connected")
            return 0
        
        march_count = 2
        
        # Check for March1
        march1_config = self.config.get("ui_elements", {}).get("MarchNb1")
        if march1_config:
            found_march1, _ = self.bot.detect_ui_element_in_area(
                march1_config["image_path"],
                march1_config.get("search_area"),
                march1_config.get("threshold", 0.5)
            )
            if found_march1:
                march_count -= 1
                self.log("✓ March1 slot available")
            else:
                self.log("✗ March1 slot not available")
        
        # Check for March2
        march2_config = self.config.get("ui_elements", {}).get("MarchNb2")
        if march2_config:
            found_march2, _ = self.bot.detect_ui_element_in_area(
                march2_config["image_path"],
                march2_config.get("search_area"),
                march2_config.get("threshold", 0.6)
            )
            if found_march2:
                march_count -= 1
                self.log("✓ March2 slot available")
            else:
                self.log("✗ March2 slot not available")
        
        self.log(f"Total available marches: {march_count}")
        return march_count
    
    def explore_ruins_flow(self):
        """Main ruin exploration flow"""
        self.log("🗺️ Starting ruin exploration flow...")
        
        # Step 1: Go to map
        # if self.click_element("map_button"):
        #     time.sleep(3)  # Wait for map to load

        available_marches = self.count_available_marches()
        self.log(f"Available marches: {available_marches}")
        
        if available_marches == 0:
            return False
        
        explored_ruins = self.load_explored_ruins()
        ruin_coords = self._load_ruin_coordinates()
        self.log(f"Previously explored ruins: {len(explored_ruins)}")
        
        marches_used = 0
        total_explored = 0
        
        # Step 5: Iterate through all areas and coordinates
        for level, areas in ruin_coords.items():
            if marches_used >= available_marches:
                break
                
            self.log(f"🔍 Searching {level}...")
            
            for area_name, coordinates in areas.items():
                if marches_used >= available_marches:
                    break
                    
                self.log(f"  📍 Checking {area_name}")
                
                for coord in coordinates:
                    if marches_used >= available_marches:
                        break
                    
                    x, y = coord
                    coord_key = f"{x},{y}"
                    
                    # Skip if already explored
                    if coord_key in explored_ruins:
                        continue
                    
                    # Search for ruin at this coordinate
                    if self.search_ruin_at_coordinate(x, y):
                        # Successfully started exploration
                        marches_used += 1
                        total_explored += 1
                        self.log(f"✅ March {marches_used}/{available_marches} started at ({x}, {y})")

                    explored_ruins.append(coord_key)
                    self.save_explored_ruins(explored_ruins)
                    time.sleep(1)
        
        self.log(f"🎯 Ruin exploration completed!")
        self.log(f"   Marches used: {marches_used}/{available_marches}")
        self.log(f"   New ruins explored: {total_explored}")
        
        # Return to city
        time.sleep(2)
        if self.click_element("home_button"):
            self.log("✓ Returned to city")
        
        return marches_used > 0


# Example usage
if __name__ == "__main__":
    # This would be used with the MinimalBot
    print("CityManager class ready for integration")
    print("Available actions:")
    manager = CityManager(None)  # Pass actual bot instance
    for action in manager.get_available_actions():
        print(f"  - {action}")
