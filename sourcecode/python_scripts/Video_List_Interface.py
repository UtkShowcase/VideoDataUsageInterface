import pandas as pd
import numpy as np
import os
import shutil
import pathlib
import Video_Understander
import Multiprocess_Video_Managment
import cv2



class VideoListInterface(object):
    
    
    VIDEO_STORAGE_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("datastorage","videostoragelocation")
    DATABASE_FILE_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("datastorage","database","mainstoragefile.csv")
    
    
    def __init__(self):
        
        try:
            
            
            print("Reading from the Internal CSV File")
            df = pd.read_csv(VideoListInterface.DATABASE_FILE_LOCATION)
            
            
        except Exception as E:
            
            
            print(E)
            print("Error in Reading the Main CSV Storage File")
            

        columns = ["VIDEO Name","VIDEO Discription","VIDEO Download Link","Raw VIDEO Present","Raw VIDEO Location","ContaingFrameNumber VIDEO Present","ContaingFrameNumber VIDEO Location"]
        self.DF = pd.DataFrame(columns=columns)
        
        
        for _,row in df.iterrows():
            
            
            data = dict() # Empty Dictionary Which will be Used to Fill the ROWs of self.DF
            
            
            data["VIDEO Name"] = row["VIDEO Name"].strip()
            data["VIDEO Discription"] = row["VIDEO Discription"].strip()
            
             
            data["Raw VIDEO Present"],data["Raw VIDEO Location"] = self.__is_Present_As_Raw_Video__(data["VIDEO Name"])
            if data["Raw VIDEO Present"]:
                
                data["VIDEO Download Link"] = np.nan
                
            else:
                
                data["VIDEO Download Link"] = row["VIDEO Download Link"].strip()
                
            
            data["ContaingFrameNumber VIDEO Present"],data["ContaingFrameNumber VIDEO Location"] = self.__is_Present_As_ContaingFrameNumber_Video__(data["VIDEO Name"])
            
            self.DF.loc[len(self.DF)] = data
                 
    
    
    def __is_Present_As_Raw_Video__(self,video_name):
        
        video_name = video_name.lower()

        files = [fg.lower() for fg in os.listdir(VideoListInterface.VIDEO_STORAGE_LOCATION)]
        if video_name not in files:
            
            return (False,None) 
        
        else:
            
            video_folder_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath(f"{video_name}")
            
            files_with_loc = list()
            files_without_extension = list()
                
            for fg in os.listdir(video_folder_loc):
                
                files_with_loc.append(video_folder_loc.joinpath(fg))
                files_without_extension.append(fg.split(".")[0].lower())
            
            
            try:
            
            
                loc = files_without_extension.index("raw")
                return (True,files_with_loc[loc])
        
        
            except Exception as E:
                return (False,None)
            
    
    
    def __is_Present_As_ContaingFrameNumber_Video__(self,video_name):

        video_name = video_name.lower()

        files = [fg.lower() for fg in os.listdir(VideoListInterface.VIDEO_STORAGE_LOCATION)]
        if video_name not in files:
            
            return (False,None) 
        
        else:
            
            video_folder_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath(f"{video_name}")
            
            files_with_loc = list()
            files_without_extension = list()
                
            for fg in os.listdir(video_folder_loc):
                
                files_with_loc.append(video_folder_loc.joinpath(fg))
                files_without_extension.append(fg.split(".")[0].lower())
            
            
            try:
            
            
                loc = files_without_extension.index("containingframenumber")
                return (True,files_with_loc[loc])
        
        
            except Exception as E:
                return (False,None)
    

    def cal_Display(self):
        
        return self.DF[["VIDEO Name","VIDEO Discription","Raw VIDEO Present","ContaingFrameNumber VIDEO Present"]]       
    
    
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
        
        raw_video = cv2.VideoCapture(raw_video_loc)
        
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
            
            
        self.cal_Refresh_Data()
        
        
                    
                    
    def cal_Insert_All_Raw_Video_Files(self,folder_loc):
        
        
        for video in os.listdir(folder_loc):
            
            video_folder = video.split(".")[0]
            ext = video.split(".")[-1]
            
            if not self.DF["VIDEO Name"].isin([video_folder]).any():
                print(f"Include {video} in the DataBase File")
                continue
            
            video_folder_loc = VideoListInterface.VIDEO_STORAGE_LOCATION.joinpath(video_folder)
            os.makedirs(video_folder_loc,exist_ok=True)
            
            output_video_loc = video_folder_loc.joinpath(f"raw.{ext}")
            input_video_loc = pathlib.Path(folder_loc).joinpath(video)
            
            shutil.move(input_video_loc,output_video_loc)
        
        self.cal_Refresh_Data()
            
        
    def cal_Refresh_Data(self):
        
        columns = ["VIDEO Name","VIDEO Discription","VIDEO Download Link","Raw VIDEO Present","Raw VIDEO Location","ContaingFrameNumber VIDEO Present","ContaingFrameNumber VIDEO Location"]
        DF = pd.DataFrame(columns=columns)
        
        
        for _,row in self.DF.iterrows():
            
            data = dict() # Empty Dictionary Which will be Used to Fill the ROWs of self.DF
            
            
            data["VIDEO Name"] = row["VIDEO Name"].strip()
            data["VIDEO Discription"] = row["VIDEO Discription"].strip()
            
             
            data["Raw VIDEO Present"],data["Raw VIDEO Location"] = self.__is_Present_As_Raw_Video__(data["VIDEO Name"])
            if data["Raw VIDEO Present"]:
                
                data["VIDEO Download Link"] = np.nan
                
            else:
                
                data["VIDEO Download Link"] = row["VIDEO Download Link"].strip()
                
            
            data["ContaingFrameNumber VIDEO Present"],data["ContaingFrameNumber VIDEO Location"] = self.__is_Present_As_ContaingFrameNumber_Video__(data["VIDEO Name"])
            
            DF.loc[len(DF)] = data
            
        self.DF = DF
    
    
    
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
        
    
    
    def cal_Read_Data_From_File_And_Trim(self,txt_file_loc):
        
        txt_file_loc = pathlib.Path(txt_file_loc)
        
        with open(txt_file_loc,"r") as f:
            
            lines = f.readlines()
            
        for line in lines:
            
            elements = line.split(" ")
            
            video_name = str(elements[0])
            start = int(elements[1])
            end = int(elements[2])
            
            indx = int(self.DF[self.DF["VIDEO Name"] == video_name].index[0])
            
            self.cal_Trim_The_Raw_Video(indx,start,end)
            
    
                            