# 台鐵公開資料(JSON)轉換
# 這個類別主要將台鐵的JSON各車次時刻表，推算通過與停靠所有車站的時間，並且依照順序增加順序碼
# 再轉為車次會在各運行路線的時間與位置資料

import pandas as pd  
# import numpy as np
import re

# 自訂class與module
import environment_variable as ev

# 公用參數
Globals = ev.GlobalVariables()
Route = Globals.Route                   # 列車路徑基本資料
SVG_X_Axis = Globals.SVG_X_Axis         # 時間空間基本資料
LinesStations = Globals.LinesStations  # 各營運路線車站於運行圖中的位置，用於運行線的繪製

class SpaceTime:           

    def CalculateSpaceTime(self, train):

        trains_data = []                         # 台鐵各車次時刻表轉換整理後資料
        after_midnight_data = []                 # 跨午夜車次的資料

        train_id = train['TrainInfo']['TrainNo']               # 車次代碼
        car_class = train['TrainInfo']['TrainTypeID']          # 車種代碼
        line = train['TrainInfo']['RouteID']                   # 營運路線代碼
        line_dir = train['TrainInfo']['Direction']             # 順行0、逆行1
        
        # 將這個車次表定台鐵時刻表所有「停靠」車站轉出
        timetable = self._find_train_timetable(train)

        # 查詢車次會「停靠與通過」的所有車站
        passing_stations = self._find_passing_stations(timetable, line, line_dir)

        # 將車次通過車站時間轉入各營運路線的資料，設定通過車站的順序碼，並且推算跨午夜車次的距離
        operation_lines = self._time_space_to_operation_lines(passing_stations)

        # 將車次的各營運線資料整理好之後，增加到trains_data清單中
        for key, value in operation_lines['Operation_Lines'].items():
            trains_data.append([key, train_id, car_class, line, value])

        return {"Train_Data" :trains_data, "After_midnight_Data": after_midnight_data}

    # 查詢表定台鐵時刻表所有「停靠」車站，可查詢特定車次
    def _find_train_timetable(self, train_no):
        timetable = {}     

        for TimeInfos in train_no['StopTimes']:
            arrivalTime = TimeInfos.get('ArrivalTime')
            departureTime = TimeInfos.get('DepartureTime')

            if self._check_format(arrivalTime):
                arrivalTime = arrivalTime
            else:
                arrivalTime = departureTime

            if self._check_format(departureTime):
                departureTime = departureTime
            else:
                departureTime = arrivalTime

            timetable[TimeInfos['StationID']] = [ arrivalTime + ":00",
                                                  departureTime + ":00",
                                                #   TimeInfos['DepartureTime'] + ":00", 
                                                  TimeInfos['StationID'],
                                                  TimeInfos['StopSequence'],
                                                  TimeInfos['StationName']['Zh_tw']]

        return timetable  # 字典 車站ID: [到站時間, 離站時間, 車站ID, 順序, 名稱]

    # 檢查到離站時間格式
    def _check_format(self, input_string):
        pattern = r'^\d{2}:\d{2}$'
        if input_string is not None and re.match(pattern, input_string):
            return True
        else:
            return False

    # 查詢車次會「停靠與通過」的所有車站
    def _find_passing_stations(self, timetable, line, line_dir):
        _time_space = []
        for index, value in timetable.items():
            _time_space.append({'StationName': value[4], 'StationID': value[2], 'StopSequence': value[3], 'Time': float(SVG_X_Axis[value[0]])})
            _time_space.append({'StationName': value[4], 'StationID': value[2], 'StopSequence': value[3], 'Time': float(SVG_X_Axis[value[1]])})   

        return _time_space  # 清單: [車站ID, 車站名稱, 里程位置, 與下一站相差公里數], 清單: 屬於哪一個支線
         
    # 將車次通過車站時間轉入各營運路線的資料，設定通過車站的順序碼，並且推算跨午夜車次的距離
    def _time_space_to_operation_lines(self, time_space):
        _operation_lines = {}
        _after_midnight_train = {}
        stop_order = 0

        for key, value in LinesStations.items():
            _operation_lines[key] = [[], [], [], [], [], []]
        for item in time_space:
            for key, value in LinesStations.items():
                if item['StationID'] in value:
                    _operation_lines[key][0].append(item['StationName'])
                    _operation_lines[key][1].append(item['StationID'])
                    _operation_lines[key][2].append(item['Time'])
                    _operation_lines[key][3].append(float(value[item['StationID']]['SVGYAXIS']))
                    _operation_lines[key][4].append('Y')
                    _operation_lines[key][5].append(stop_order)
            stop_order += 1

        for key, value in _operation_lines.items():
            _operation_lines[key] = pd.DataFrame({"Station": value[0],
                                                  "StationID": value[1],
                                                  "Time": value[2],
                                                  "Loc": value[3],
                                                  "StopStation": value[4],
                                                  "StopOrder": value[5]})

        return {"Operation_Lines": _operation_lines, "After_Midnight_Train": _after_midnight_train}  # 本日車次運行資料, 跨午夜車次午夜後的運行資料


