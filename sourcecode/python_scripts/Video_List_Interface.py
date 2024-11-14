import pandas as pd
import numpy as np
import os
import shutil
import pathlib
import Video_Understander
import Multiprocess_Video_Managment
import cv2



class VideoListInterface(object):
    
    
    VIDEO_STORAGE_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("videostoragelocation")
    INPUT_VIDEO_FILE_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("inputdata","videofiles")
    INPUT_TRIMMING_TXT_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("inputdata","trimming.txt")
    
    
    def __init__(self):
            

        columns = ["VIDEO Name","Raw VIDEO Present","Raw VIDEO Location","ContaingFrameNumber VIDEO Present","ContaingFrameNumber VIDEO Location"]
        self.DF = pd.DataFrame(columns=columns)
        
        
        for folders in os.listdir(VideoListInterface.VIDEO_STORAGE_LOCATION):
            
            if folders == ".gitkeep":
                continue  
            
            data = dict()
            
            video_name = folders
            folder_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath(video_name)
            
            data["VIDEO Name"] = video_name
            
            loc_files = [folder_loc.joinpath(fg) for fg in os.listdir(folder_loc)]            
            name_files = [pathlib.Path(fg).stem for fg in os.listdir(folder_loc)]
            
            if "raw" in name_files:
                
                data["Raw VIDEO Present"] = True
                
                index = name_files.index("raw")
                
                data["Raw VIDEO Location"] = loc_files[index]
            
            else:
                
                print("Errorr Raw Video Missing!!!!")
                raise Exception  
                
                
            if "containingframenumber" in name_files:
                
                data["ContaingFrameNumber VIDEO Present"] = True
                
                index = name_files.index("containingframenumber")
                
                data["ContaingFrameNumber VIDEO Location"] = loc_files[index]
            
            else:
                
                data["ContaingFrameNumber VIDEO Present"] = False
                
                data["ContaingFrameNumber VIDEO Location"] = None
                
            
            self.DF.loc[len(self.DF)] = data
            
        self.__initialize_Trimmimg_Txt_File__()
            
            

    def __initialize_Trimmimg_Txt_File__(self):
        
        data = dict()
        
        with open(VideoListInterface.INPUT_TRIMMING_TXT_LOCATION,"r") as f:
            
            lines = f.readlines()
            
        for line in lines:
            
            if " " in line:
            
                indx = line.index(" ")
                
                key = line[:indx].strip("\n")
                value = line[indx:].strip("\n")
                
                data[key] = value
            else:
                
                line = line.strip("\n")
                data[line] = ""

        with open(VideoListInterface.INPUT_TRIMMING_TXT_LOCATION,"w") as f:
        
            for _,row in self.DF.iterrows():
            
                video_name = row["VIDEO Name"]
                
                if video_name in data:
                    
                    insert_text = f"{video_name}{data[video_name]}"
                
                else:
                    
                    insert_text = video_name
                
                if _ == 0:
                    insert_line = f"{insert_text}"
                else:
                    insert_line = f"\n{insert_text}"
                
                f.write(insert_line)



    def __check_FPS_Is_Workable_Or_Not__(self,video_loc):
        
        video = cv2.VideoCapture(video_loc)
        
        fps = video.get(cv2.CAP_PROP_FPS) 
        
        fps_str = str(fps)
        idx = fps_str.index(".")
        fg = int(fps_str[idx+1:])
        
        if fg == 0:
            
            return True
        
        else: 
        
            return False 



    def __check_Raw_Video_Is_Ready__(self,raw_video_loc):
        
        result = self.__check_FPS_Is_Workable_Or_Not__(raw_video_loc)
        
        return result
    
    

    def __check_Both_Videos_Are_Ready__(self,raw_video_loc,containingframeno_video_loc):
        
        raw_video = cv2.VideoCapture(raw_video_loc)
        containingframe_video = cv2.VideoCapture(containingframeno_video_loc)
        
        raw_video_fps = raw_video.get(cv2.CAP_PROP_FPS)
        containingframe_video_fps = containingframe_video.get(cv2.CAP_PROP_FPS)
        
        if raw_video_fps != containingframe_video_fps:
            
            return False
        
        else:
            
            return self.__check_FPS_Is_Workable_Or_Not__(raw_video_loc)



    def __convert_Raw_Video_Into_Worlable__(self,raw_video_loc):
            
        output_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath("fg.mp4")
            
        Multiprocess_Video_Managment.process_And_Write_Videos(raw_video_loc,output_loc)
            
        os.remove(raw_video_loc)
            
        os.rename(output_loc,raw_video_loc) 



    def __create_The_ContainingFrameNumber_Video__(self,idx):
        
        obj = self.cal_Work_On_Video(idx)
        
        try:
            a = obj.containgframenumber_video_location  
        
        except Exception as e:
            pass
        
        else:
            os.remove(obj.containgframenumber_video_location)
            
        obj.cal_create_Video_ContaingFrameNumber_Type()



    def cal_Insert_All_Raw_Video_Files(self):
        
        folder_loc = VideoListInterface.INPUT_VIDEO_FILE_LOCATION
        
        for video in os.listdir(folder_loc):
            
            if video == ".gitkeep":
                continue
            
            video_folder = pathlib.Path(video).stem
            ext = pathlib.Path(video).suffix
            
            video_folder_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath(video_folder)
            os.makedirs(video_folder_loc,exist_ok=True)
            
            output_video_loc = video_folder_loc.joinpath(f"raw{ext}")
            input_video_loc = pathlib.Path(folder_loc).joinpath(video)
            
            shutil.move(input_video_loc,output_video_loc)
        
        self.__refresh_Data__()



    def cal_Display(self):
        
        return self.DF[["VIDEO Name","Raw VIDEO Present","ContaingFrameNumber VIDEO Present"]]       
    
  
    
    def cal_Work_On_Video(self,row_number):
        
        
        row = self.DF.iloc[row_number]
        
        fg = dict()

        
        fg["creator_list_instance"] = self
        fg["video_name"] = row["VIDEO Name"]
        
        
        if row["Raw VIDEO Present"] == True:
            
            
            fg["raw_video_loc"] = row["Raw VIDEO Location"]
        
        
        else:
            
            print("ERROR!!!\nRaw Video Location Not Present so cannot Create Video Understander Object")
            


        if row["ContaingFrameNumber VIDEO Present"] == True:
            
            
            fg["containgframenumber_video_loc"] = row["ContaingFrameNumber VIDEO Location"]


        return Video_Understander.VideoUnderstander(fg)



    def __refresh_Data__(self):
        
        columns = ["VIDEO Name","Raw VIDEO Present","Raw VIDEO Location","ContaingFrameNumber VIDEO Present","ContaingFrameNumber VIDEO Location"]
        self.DF = pd.DataFrame(columns=columns)
        
        
        for folders in os.listdir(VideoListInterface.VIDEO_STORAGE_LOCATION):
            
            if folders == ".gitkeep":
                continue  
            
            
            data = dict()
            
            
            video_name = folders
            folder_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath(video_name)
            
            data["VIDEO Name"] = video_name
            
            loc_files = [folder_loc.joinpath(fg) for fg in os.listdir(folder_loc)]            
            name_files = [pathlib.Path(fg).stem for fg in os.listdir(folder_loc)]
            
            if "raw" in name_files:
                
                data["Raw VIDEO Present"] = True
                
                index = name_files.index("raw")
                
                data["Raw VIDEO Location"] = loc_files[index]
            
            else:
                
                print("Errorr Raw Video Missing!!!!")
                raise Exception  
                
                
            if "containingframenumber" in name_files:
                
                data["ContaingFrameNumber VIDEO Present"] = True
                
                index = name_files.index("containingframenumber")
                
                data["ContaingFrameNumber VIDEO Location"] = loc_files[index]
            
            else:
                
                data["ContaingFrameNumber VIDEO Present"] = False
                
                data["ContaingFrameNumber VIDEO Location"] = None
                
            
            self.DF.loc[len(self.DF)] = data

        self.__initialize_Trimmimg_Txt_File__()
    
    
        
    def cal_Make_Every_Video_Ready_For_Working(self):
        
        for indx,row in self.DF.iterrows():
            
            print("<----------------------------------------------------------->")
            print(f"Checking Video for {row["VIDEO Name"]}")
            result = False
            
            if row["Raw VIDEO Present"] == True and row["ContaingFrameNumber VIDEO Present"] == False:
                
                print(f"Raw Video Present and ContainingFrameNumber Video Not Present")
                raw_video_loc = row["Raw VIDEO Location"]
                
                result = self.__check_Raw_Video_Is_Ready__(raw_video_loc)
                
                if result == False:
                    
                    print(f"Converting the Raw Video")
                    self.__convert_Raw_Video_Into_Worlable__(raw_video_loc=raw_video_loc)
                
                print("Making the ContainingFrame Number Video")
                self.__create_The_ContainingFrameNumber_Video__(indx)
                
            elif row["Raw VIDEO Present"] == True and row["ContaingFrameNumber VIDEO Present"] == True:
                
                print(f"Raw Video Present and ContainingFrameNumber Video Present")
                raw_video_loc = row["Raw VIDEO Location"]
                containingframeno_video_loc = row["ContaingFrameNumber VIDEO Location"]
                
                result = self.__check_Both_Videos_Are_Ready__(raw_video_loc,containingframeno_video_loc)
                print(result)
                
                if result == False:
                    
                    print("Creating The Raw Video")
                    self.__convert_Raw_Video_Into_Worlable__(raw_video_loc)
                    print("Creating the ContainingFrameNumber Video")
                    self.__create_The_ContainingFrameNumber_Video__(indx)            

            print("<------------------------------------------------------------------------------>")
            
            
        self.__refresh_Data__()
        
    
    
    def cal_Trim_The_Raw_Video(self,indx,start_frame_number,end_frame_number):
        
        row = self.DF.iloc[indx]
        
        raw_video_loc = row["Raw VIDEO Location"]
        
        output_video_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath("fg.mp4")
        
        print(f"Raw Video Loc :- {raw_video_loc}")
        print(f"Output Video Loc :- {output_video_loc}")
        
        Multiprocess_Video_Managment.process_And_Write_Videos(raw_video_loc,output_video_loc,start=start_frame_number,end=end_frame_number)
        
        os.remove(raw_video_loc)
        
        os.rename(output_video_loc,raw_video_loc)
            
        self.__create_The_ContainingFrameNumber_Video__(indx)
        
    
    
    def cal_Read_Data_From_File_And_Trim(self):
        
        txt_file_loc = pathlib.Path(self.INPUT_TRIMMING_TXT_LOCATION)
        
        with open(txt_file_loc,"r") as f:
            
            lines = f.readlines()
            
        for line in lines:
            
            if " " not in line:
                continue
            
            elements = line.split(" ")
            
            video_name = str(elements[0])
            start = int(elements[1])
            end = int(elements[2])
            
            indx = int(self.DF[self.DF["VIDEO Name"] == video_name].index[0])
            
            self.cal_Trim_The_Raw_Video(indx,start,end)

            
    
                            