import pathlib
import cv2
from enum import Enum
import tabulate
import Multiprocess_Video_Managment
import os


class Resolution(Enum):
    
    
    res_1920_1080 = 0
    res_1280_720 = 1


class VideoTypes(Enum):
    
    
    RAW = 0
    CONTAININGFRAMENUMBER = 1

    
    
class VideoUnderstander(object):



    # Locatios Of Internally Used Directory Structure
    VIDEO_STORAGE_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("videostoragelocation")
    WORKING_SPACE_LOCATION = pathlib.Path.cwd().parent.parent.joinpath("workingdir")
    
    
    
    def __init__(self,creation_data):
        '''
        Parameterized Constructor
        Input Parameteres:-
        <>
        '''



        if "creator_list_instance" in creation_data:


            VideoUnderstander.CREATOR_LIST_INSTANCE = creation_data["creator_list_instance"]
        else:


            raise Exception("Pass a Creator List Interafce Object Refrence !!!!")


        if "video_name" in creation_data:
            
            
            self.video_name = creation_data["video_name"]
        else:
            
            
            raise Exception("Pass The Video Name !!!!!")
            
        
        if "raw_video_loc" not in creation_data:
            raise Exception("Not a Single Location Provided")


        else:
            
            
            self.raw_video_location = creation_data["raw_video_loc"]
            try:
                
                
                video = cv2.VideoCapture(creation_data["raw_video_loc"])
                
            except Exception as E:
                
                
                print(E)
                print("Raw Video Location not READABLE!")

        
        if "containgframenumber_video_loc" in creation_data:
            
            
            self.containgframenumber_video_location = creation_data["containgframenumber_video_loc"]
            try:
                
                
                video = cv2.VideoCapture(creation_data["containgframenumber_video_loc"])
            except Exception as E:
                
                
                print(E)
                print("ContaingFramenumber Video Location not READABLE!")
            
        
        self.no_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = video.get(cv2.CAP_PROP_FPS)
        self.width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.hieght = video.get(cv2.CAP_PROP_FRAME_HEIGHT)


        if self.width == 1920 and self.hieght == 1080:
            
            
            self.resolution = Resolution.res_1920_1080

        elif self.width == 1280 and self.hieght == 720:
            
            
            self.resolution = Resolution.res_1280_720

        self.CURRENT_VIDEO_STATE = VideoTypes.RAW
        
        video.release()
    
    
    
    def __label_Frame_With_Frame_Number__(self,frame,frame_number):
        
        
        if self.resolution == Resolution.res_1920_1080:
            
            
            x1 = 1000
            y1 = 30
            x2 = 1150
            y2 = 90


        if self.resolution ==  Resolution.res_1280_720:
            
            
            x1 = 720
            y1 = 30
            x2 = 870
            y2 = 90


        cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,255),-1)
        cv2.putText(frame,f"{frame_number}",(x1+3,(y2-y1)),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
        return frame
    
    
    
    def __extract_Frames_From_Given_State__(self,start,end,project_name,state):
        
        
        if state == VideoTypes.RAW:
            
            video_loc = self.raw_video_location
          
                
        if state == VideoTypes.CONTAININGFRAMENUMBER:
            
          video_loc = self.containgframenumber_video_location
        
        
        print("<------------------------------------------------------->")
        print(f"Creating Frames for Video:- {self.video_name}\nBetween Frame Number {start} - {end}nFor Type {self.CURRENT_VIDEO_STATE}")        
        output_folder_loc = VideoUnderstander.WORKING_SPACE_LOCATION.joinpath(f"{project_name}")
        Multiprocess_Video_Managment.process_And_Write_Frames(video_loc, start, end, output_folder_loc)
        print("<------------------------------------------------------->")
    
        
        
    def __repr__(self):
         
        return self.video_name
    
    
    
    def cal_display_Information(self):
        
        
        
        table = [["Name",self.video_name],
                 ["FPS",self.fps],
                 ["Frames Count",self.no_frames],
                 ["Width",self.width],
                 ["Hieght",self.hieght],
                 #["Resolution",self.resolution]
                ]
        
        
        print(tabulate.tabulate(table,tablefmt='fancy_grid'))
    
        
    
    def cal_change_State_To_Frame_Type(self):
        
        self.CURRENT_VIDEO_STATE = VideoTypes.CONTAININGFRAMENUMBER
        
    
    
    def cal_change_State_To_Raw_Type(self):
        
        self.CURRENT_VIDEO_STATE = VideoTypes.RAW
    
        
    
    def cal_create_Video_ContaingFrameNumber_Type(self):



        output_loc = VideoUnderstander.VIDEO_STORAGE_LOCATION.joinpath(f"{self.video_name}","containingframenumber.mp4")

        print("<------------------------------------------------------->")
        print(f"Creating ContaingFrameNumber Video for {self.video_name} and output_location_is = {output_loc}")
        Multiprocess_Video_Managment.process_And_Write_Videos(self.raw_video_location,output_loc,self.__label_Frame_With_Frame_Number__)
        print(f"Created ContaingFrameNumber Video for {self.video_name}")
        print("<------------------------------------------------------->")
        
   
    
    def cal_Extract_Frames_From_Raw_Video(self,start,end,project_name):
        
        self.__extract_Frames_From_Given_State__(start=start,end=end,project_name=project_name,state=VideoTypes.RAW)
        
    
    
    def cal_Extract_Frames_From_ContainingFrameNumber_Video(self,start,end,project_name):
        
        self.__extract_Frames_From_Given_State__(start=start,end=end,project_name=project_name,state=VideoTypes.CONTAININGFRAMENUMBER)
    
    
        
    def cal_Extract_Frame_From_All_Types(self,start,end,project_name):
        
        raw_project_name = f"{project_name}__RAW"
        self.__extract_Frames_From_Given_State__(start=start,end=end,project_name=raw_project_name,state=VideoTypes.RAW)
        
        containingframenumber_project_name = f"{project_name}__CONTAININGFRAMENUMBER"
        self.__extract_Frames_From_Given_State__(start=start,end=end,project_name=containingframenumber_project_name,state=VideoTypes.CONTAININGFRAMENUMBER)
      
        
    
    def cal_Read_From_File_And_Extract_Frames(self,txt_file_loc):
        
        txt_file_loc = pathlib.Path(txt_file_loc)
        
        with open(txt_file_loc,"r") as f:
            
            lines = f.readlines()
        
        
        count = 0
            
        for line in lines:
            
            elements = line.split()
            
            start = int(elements[0])
            end = int(elements[1])
            
            files = os.listdir(VideoUnderstander.WORKING_SPACE_LOCATION)
            
            while True:
                
                output_folder_name = f"{self.video_name}__{count}"
                
                if output_folder_name not in files:
                    count += 1
                    break
                
                count += 1
                
            
            self.cal_Extract_Frame_From_All_Types(start,end,output_folder_name)
            
