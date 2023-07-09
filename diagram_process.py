# 台鐵資料轉換後繪製程序
from math import dist
import queue

# 自訂class與module
import environment_variable as ev
import diagram as dm

# 公用參數
Globals = ev.GlobalVariables()

# 繪製各路線的車次線
def draw(all_trains, location, date):
    diagrams = {} # 各營運線運行圖

    for key, value in Globals.OperationLines.items():
        diagrams[key] = dm.Diagram(Globals.LinesStationsForBackground[key],
                                    "{0}/{1}/{2}".format(location, value['FOLDER'], value['PREFIX']),
                                    date,
                                    key,
                                    600 * (len(Globals.DiagramHours) - 1) + 100,
                                    int(value["MAX_X_AXIS"]),
                                    Globals.DiagramHours)

    for train in all_trains:
        for line_kind, train_id, car_class, line_dir, train_time_space in train:
            set_train_path(line_kind, train_id, car_class, train_time_space, diagrams)

    for key, value in diagrams.items():
        value.save_file()

# 車次線路徑與車次號標註
def set_train_path(line_kind, train_id, car_class, train_time_space, diagrams):
    color = Globals.CarKind.get(car_class, 'special')
    coordinates = queue.Queue()  # 用來置放每一個轉折點的座標值
    path = "M"
    for item_index, row in train_time_space.iterrows():        
        if row['StopStation'] != -1 or Globals.LinesStationsForBackground[line_kind][row['StationID']]['TERMINAL'] == "Y":
            x = round(row['Time'] * 5 - 600 * Globals.DiagramHours[0] + 50, 4)
            y = round(row['Loc'] + 50, 4)
            path += str(x) + ',' + str(y) + ' '
            coordinates.put((x, y)) 

    # 依據每一個轉折點座標，計算每一個轉折點之間的長度
    coordinates_pairs_temp = []          
    coordinates_distance = []   # 用來置放每一個轉折點之間的長度
    while not coordinates.empty():  
        if len(coordinates_pairs_temp) == 2:            
            coordinates_distance.append(dist(coordinates_pairs_temp[0], coordinates_pairs_temp[1]))
            coordinates_pairs_temp[0] = coordinates_pairs_temp[1]
            coordinates_pairs_temp[1] = coordinates.get()
        elif len(coordinates_pairs_temp) == 1: 
            coordinates_pairs_temp.append(coordinates.get())
        elif len(coordinates_pairs_temp) == 0: 
            coordinates_pairs_temp.append(coordinates.get())
    if len(coordinates_pairs_temp) == 2:
        coordinates_distance.append(dist(coordinates_pairs_temp[0], coordinates_pairs_temp[1]))
    
    # 區間車標號方式：各段長度長於60，偶數位的進行標註，其他車種：100-500的長度在中間標註，大於500則是在中間標註兩次
    text_position = []   # 用來置放標號定位點
    accumulate_dist = 0  # 所有轉折點的長度累進
    if color == "local":       
        new_text_position = []
        for item in coordinates_distance:        
            if item > 60:
                pos = accumulate_dist + item / 4
                text_position.append(pos)
            accumulate_dist += item
        for i in range(0, len(text_position)):        
            if i % 2 == 0:
                new_text_position.append(text_position[i])
        text_position = new_text_position
    else:
        for item in coordinates_distance:        
            if item > 60 and item < 100:
                text_position.append(0)
            elif item >= 100 and item <= 500:
                pos = accumulate_dist + item / 2
                text_position.append(pos)
            elif item > 500:
                for i in range(1, 3):
                    pos = accumulate_dist + i * (item / 3)
                    text_position.append(pos)
            accumulate_dist += item

    diagrams[line_kind].draw_line(train_id, path, text_position, color)
