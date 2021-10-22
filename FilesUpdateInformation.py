import os,sys
import time
import csv
import datetime

Files_Path = 'D:\Temp_Regular_Files\测试文件' #填入要查看更新信息的文件夹名称。
Log_Path = 'D:\Temp_Regular_Files\测试文件日志' #填入存放日志和文件树的文件夹名称。
Updater_Name = 'QwQ' #进行更新操作的人的名称。
Log_Filename = 'log.txt'
Log_Logic_Judgment = '2' # 填入日志记录采取的逻辑方式。

Chinese_Files_Path = Files_Path # unicode(Files_Path,'utf-8')
Chinese_Log_Path = Log_Path # unicode(Log_Path,'utf-8')

##### 以上部分用于信息的填写 #####

class File_Tree():
    def __init__ (self,File_Name,Creation_Time,Change_Time,File_Path,Get_Creation_Time,Get_Change_Time):
        self.File_Name = File_Name
        self.Creation_Time = Creation_Time
        self.Change_Time = Change_Time
        self.File_Path = File_Path
        self.Get_Creation_Time = Get_Creation_Time
        self.Get_Change_Time = Get_Change_Time

##### 以上部分用于类的建立 #####


def Get_Filelist(Dir, Filelist):
# 用递归的形式完成遍历。Dir路径，Filelist文件列表。
    NextDir = Dir
    if os.path.isfile(Dir):
        File_Tree_1 = File_Tree('','','','',0,0) 
        File_Tree_1.File_Name = os.path.basename(Dir) #文件名
        File_Tree_1.File_Path = Dir #文件路径
        File_Tree_1.Creation_Time = time.asctime(time.localtime(os.path.getctime(Dir)))#创建时间
        File_Tree_1.Change_Time = time.asctime(time.localtime(os.path.getmtime(Dir)))#修改时间
        File_Tree_1.Get_Creation_Time = os.path.getctime(Dir) #未转化的创建时间
        File_Tree_1.Get_Change_Time = os.path.getmtime(Dir) #未转化的更改时间
        Filelist.append(File_Tree_1)
        #该方法将会返回路径，若仅仅返回文件名，使用方法Filelist.append(os.path.basename(Dir))。
    elif os.path.isdir(Dir):
        for s in os.listdir(Dir):
            # 若需忽略特定文件夹，使用以下代码 if s == "xxx":continue
            NextDir=os.path.join(Dir,s)
            Get_Filelist(NextDir, Filelist)
    return Filelist

if __name__ =='__main__' :
 
    Now_File_List = Get_Filelist(Chinese_Files_Path, [])
 
    print(len(Now_File_List))
 
    for e in Now_File_List:
        print(e.File_Name)
        print (e.Creation_Time)
        print(e.Change_Time)
        print(e.File_Path)
        print(e.Get_Creation_Time)
        print(e.Get_Change_Time)

print('----------')

##### 以上部分为遍历文件夹的自定义函数 #####

Log_Files_List = Get_Filelist(Chinese_Log_Path,[]) # 读取日志与文件树文件夹的文件列表

Log_Files_List_Sorted = sorted(Log_Files_List,key = lambda x:x.Get_Change_Time,reverse=True) 
    # 按照时间顺序排列，越晚创建越靠前

for e in Log_Files_List_Sorted:
    print(e.File_Name)
    print(e.Creation_Time)
    print(e.Change_Time)
    print(e.File_Path)
    print(e.Get_Creation_Time)
    print(e.Get_Change_Time)

if Log_Files_List_Sorted == []:
    #文件夹下没有历史文件树。
    Flag_File_Tree = 0
    Empty_File_Creation_Path = os.path.join(Log_Path,'0.csv')
    open(Empty_File_Creation_Path,'w')
else:
    #存在历史文件树。
    Flag_File_Tree = 1

Elements_Number = 0
for Elements in Log_Files_List_Sorted:
    if Elements.File_Name == Log_Filename:
        break
    else:
        Elements_Number = Elements_Number + 1 

Log_Files_List_Sorted_Remove = Log_Files_List_Sorted

if Elements_Number != len(Log_Files_List_Sorted_Remove):
    Log_Files_List_Sorted_Remove.pop(Elements_Number)
# 忽略列表中作为日志存在的log.txt文件

if Flag_File_Tree == 1:
    Histroy_File_Path = Log_Files_List_Sorted_Remove[0].File_Path
else:
    Histroy_File_Path = Empty_File_Creation_Path

##### 以上部分用于选出最新（晚）的历史文件树。 #####

csv_History_List = []


print("历史文件树记录")
csv_reader=csv.reader(open(Histroy_File_Path,encoding='utf-8'))
for row in csv_reader:
    print(row)
    File_Tree_2 = File_Tree(row[0],row[1],row[2],row[3],row[4],row[5])
    csv_History_List.append(File_Tree_2)
#读取csv文件中的信息。

##### 以上部分用于查询历史文件树，将其保存为类。 #####

# Now_File_List当前。 csv_History_List历史。
Now_List_Length = len(Now_File_List) #当前文件总数。
csv_History_Length = len(csv_History_List) #历史文件总数。

File_Change_Type = 0
# 文件变更类型结论
# 0 不变
# 1 删除
# 2 新建
# 3 更新
# 4 移动
# 5 移动且更新
# 6 回朔
# 7 移动且回朔
# -1 留空

class File_Change_Record ():
    def __init__(self,Change_Type_Record,Now_List_Number,History_List_Number):
        self.Change_Type_Record = Change_Type_Record # 文件变更类型记录
        self.Now_List_Number = Now_List_Number # 位于当前列表的位置。-1则视作留空。
        self.History_List_Number = History_List_Number # 位于历史列表的位置。-1则视作留空。 

File_Change_Record_List = [] # 用于记录更改类型的文件。


# 综合逻辑检索1
def Comprehensive_Logical_Judgment_1():
    global File_Change_Record_List
    File_Change_Type = -1 
#    Elements_Counter = 0
    Filename_Same_Flag = [] # 记录所有同名文件在历史文件树中的位置。

    # 新文件。
    for index_1 , Now_File in enumerate(Now_File_List,start=0): # 以当前列表中的每一个元素遍历。
        Now_File_Change_Record_Temp = File_Change_Record(-1,-1,-1) # 新建一个实例。
        Filename_Same_Flag = [] # 清空上一次的历史同名文件记录。
        File_Change_Type = -1 

        Now_Filename = Now_File.File_Name

#        Elements_Counter_2 = 0 
        for index_2,History_File in enumerate(csv_History_List): # 检测同名文件。
            if Now_Filename == History_File.File_Name:
                Filename_Same_Flag.append(index_2)
#            Elements_Counter_2 = Elements_Counter_2 + 1 

        if Filename_Same_Flag == []: # 如果没有相同文件名则视为新建。
            Now_File_Change_Record_Temp.Change_Type_Record = 2 # 2 新建
            Now_File_Change_Record_Temp.Now_List_Number = index_1 # 记录在当前文件树列表中的位置。

        if len(Filename_Same_Flag) >= 1: # 如果存在一个或多个相同文件名。
            for History_File_Number in range(len(Filename_Same_Flag)):
                History_File_Same_Name = csv_History_List[Filename_Same_Flag[History_File_Number]]
                if Now_File.File_Path == History_File_Same_Name.File_Path: # 若为同路径。
                    if str(Now_File.Get_Change_Time) == str(History_File_Same_Name.Get_Change_Time): # 同路径且同修改时间。
                        Now_File_Change_Record_Temp.Change_Type_Record = 0 # 0 不变
                    elif str(Now_File.Get_Change_Time) != str(History_File_Same_Name.Get_Change_Time): # 同路径且不同修改时间。
                        Now_File_Change_Record_Temp.Change_Type_Record = 3 # 3 更新
                        Now_File_Change_Record_Temp.Now_List_Number = index_1 # 记录在当前文件树列表中的位置。
                elif Now_File.File_Path != History_File_Same_Name.File_Path: # 若为不同路径。
                    if str(Now_File.Get_Change_Time) == str(History_File_Same_Name.Get_Change_Time) : # 同修改时间
                        if str(Now_File.Get_Creation_Time) == str(History_File_Same_Name.Get_Creation_Time) : # 同创建时间
                            Now_File_Change_Record_Temp.Change_Type_Record = 4 # 4 移动
                            Now_File_Change_Record_Temp.Now_List_Number = index_1 # 记录在当前文件树列表中的位置。
                    elif str(Now_File.Get_Change_Time) != str(History_File_Same_Name.Get_Change_Time) : #不同修改时间
                        if str(Now_File.Get_Creation_Time) != str(History_File_Same_Name.Get_Creation_Time) : #不同创建时间
                             Now_File_Change_Record_Temp.Change_Type_Record = 2

        if Now_File_Change_Record_Temp.Change_Type_Record != 0 and Now_File_Change_Record_Temp.Change_Type_Record != -1 :
            File_Change_Record_List.append(Now_File_Change_Record_Temp) # 如果不是不变或者留空，则记录。
        
#        Elements_Counter = Elements_Counter + 1 


        
    #旧文件 逻辑1-2
    for index_1,History_File in enumerate(csv_History_List):
        File_Change_Type = -1 
        History_File_Change_Record_2 = File_Change_Record(-1,-1,-1) # 新建一个实例。
        File_Path_Same_Flag = [] # 清空上一次的历史同名文件记录。
        Histroy_File_Path = History_File.File_Path

        for Now_File_3 in Now_File_List:
            if str(Histroy_File_Path) == str(Now_File_3.File_Path):
                File_Path_Same_Flag.append(index_1)
        
        if File_Path_Same_Flag == []: # 若没有同名，则视为删除或被移动。
            History_File_Change_Record_2 = File_Change_Record(1,-1,index_1)
            File_Change_Record_List.append(History_File_Change_Record_2)

def Comprehensive_Logical_Judgment_2():
    global File_Change_Record_List
    File_Change_Type = -1 
    Filename_Same_Flag = [] # 记录所有同名文件在历史文件树中的位置。
    File_Path_Same_Flag = [] # 记录所有同路径文件在历史文件树中的位置。

    # 新文件 逻辑1-2
    for index_1 , Now_File in enumerate(Now_File_List,start=0): 
        Now_File_Change_Record_Temp = File_Change_Record(-1,-1,-1)
        File_Path_Same_Flag = [] #清空上一次的历史同路径文件记录。

        for index_2,History_File in enumerate(csv_History_List): # 检测同路径文件。
            if Now_File.File_Path == History_File.File_Path:
                File_Path_Same_Flag.append(index_2)
        if File_Path_Same_Flag == []: # 如果没有相同文件路径则视为新建。
            Now_File_Change_Record_Temp.Change_Type_Record = 2 # 2 新建
            Now_File_Change_Record_Temp.Now_List_Number = index_1 # 记录在当前文件树列表中的位置。
        elif len(File_Path_Same_Flag) >= 1 :
            History_File_Same_Name = csv_History_List[File_Path_Same_Flag[0]]
            if str(Now_File.Get_Change_Time) !=  str(History_File_Same_Name.Get_Change_Time):
                Now_File_Change_Record_Temp.Change_Type_Record = 3 # 3 更新
                Now_File_Change_Record_Temp.Now_List_Number = index_1 # 记录在当前文件树列表中的位置。
        
        if Now_File_Change_Record_Temp.Change_Type_Record != 0 and Now_File_Change_Record_Temp.Change_Type_Record != -1 :
            File_Change_Record_List.append(Now_File_Change_Record_Temp) # 如果不是不变或者留空，则记录。


    #旧文件 逻辑1-2
    for index_1,History_File in enumerate(csv_History_List):
        File_Change_Type = -1 
        History_File_Change_Record_2 = File_Change_Record(-1,-1,-1) # 新建一个实例。
        File_Path_Same_Flag = [] # 清空上一次的历史同路径文件记录。
        Histroy_File_Path = History_File.File_Path

        for Now_File_3 in Now_File_List:
            if str(Histroy_File_Path) == str(Now_File_3.File_Path):
                File_Path_Same_Flag.append(index_1)
        
        if File_Path_Same_Flag == []: # 若没有同名，则视为删除或被移动。
            History_File_Change_Record_2 = File_Change_Record(1,-1,index_1)
            File_Change_Record_List.append(History_File_Change_Record_2)






if Log_Logic_Judgment == '1':
    Comprehensive_Logical_Judgment_1()
elif Log_Logic_Judgment == '2':
    Comprehensive_Logical_Judgment_2()


##### 以上部分用于将历史文件树与当前文件树进行对比。寻找文件的更新动作。 #####


Log_txt_Path = os.path.join(Chinese_Log_Path,Log_Filename)

with open(Log_txt_Path,'a',encoding='utf-8') as f:
    f.write('\n')
    f.write("更新者:")
    f.write(Updater_Name)
    f.write('\n')
    Log_Now_Time = str(datetime.datetime.now())
    f.write(Log_Now_Time)
    f.write('\n')
    for Changed_File in File_Change_Record_List:
        if Changed_File.Change_Type_Record == 1: # 删除
            Delete_Filename = csv_History_List[Changed_File.History_List_Number].File_Name
            Delete_Path = csv_History_List[Changed_File.History_List_Number].File_Path
            f.write("被删除或移动至其他位置：")
            f.write(Delete_Filename)
            f.write("，文件路径为：")
            f.write(Delete_Path)
            f.write('\n')
        elif Changed_File.Change_Type_Record == 2: # 新建
            Create_Filename = Now_File_List[Changed_File.Now_List_Number].File_Name
            Create_Path =  Now_File_List[Changed_File.Now_List_Number].File_Path
            f.write("新建了文件：")
            f.write(Create_Filename)
            f.write("，文件路径为：")
            f.write(Create_Path)
            f.write('\n')
        elif Changed_File.Change_Type_Record == 3: # 修改
            Revise_Filename = Now_File_List[Changed_File.Now_List_Number].File_Name
            Revise_Path =  Now_File_List[Changed_File.Now_List_Number].File_Path
            Revise_Change_Time =  Now_File_List[Changed_File.Now_List_Number].Change_Time
            f.write("修改了文件：")
            f.write(Revise_Filename)
            f.write("修改时间为：")
            f.write(Revise_Change_Time)
            f.write("文件路径为：")
            f.write(Revise_Path)
            f.write('\n')
        elif Changed_File.Change_Type_Record == 4: # 移动
            Move_Filename = Now_File_List[Changed_File.Now_List_Number].File_Name
            Move_Path =  Now_File_List[Changed_File.Now_List_Number].File_Path
            f.write("移动了文件：")
            f.write(Move_Filename)
            f.write("，文件路径为：")
            f.write(Move_Path)
            f.write('\n')


##### 以上部分用于将变更写入日志文件。 #####

Complete_Str_Now_Time = str(datetime.datetime.now())
Char_Number = 0 
for Char in Complete_Str_Now_Time:
    if Char == '.':
        break
    else:
        Char_Number = Char_Number + 1
Short_Str_Now_Time = Complete_Str_Now_Time[0:Char_Number] #去掉秒后的精确内容
Short_Str_Now_Time_RC = ''
for Char in Short_Str_Now_Time:
    if Char != ':':
        Short_Str_Now_Time_RC = Short_Str_Now_Time_RC + Char
    else:
        Short_Str_Now_Time_RC = Short_Str_Now_Time_RC + '-'
#将冒号转变为短杠符号。作为文件名不会出现报错。


Now_Time = Short_Str_Now_Time_RC+'.csv' #获取当前时间。
New_File_Tree_Path = os.path.join(Chinese_Log_Path,Now_Time) #最新文件树创建时的文件路径。
print(New_File_Tree_Path)

# file = open(New_File_Tree_Path, 'w')
# Now_Time_Filename = str(datetime.datetime.now())


#创建文件列表
with open(New_File_Tree_Path,'a',encoding='utf-8',newline='') as f :
    csv_writer = csv.writer(f)
    for e in Now_File_List:
        csv_writer.writerow([str(e.File_Name),str(e.Creation_Time),str(e.Change_Time),str(e.File_Path),str(e.Get_Creation_Time),str(e.Get_Change_Time)])


##### 以上部分用于创建本次的历史文件树 #####

##### 以上部分用于删除辅助程序运行创建的"0.csv"文件





