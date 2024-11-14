import os
import cv2
import multiprocessing as mp
import subprocess as sp
import time
import threading


def process_Video_for_Each_Process(video_loc,start,end,process_func=None):
    '''
    This Method Which will be used By Each Indivivual Process
    It will create a Video form the Input Video from start(Frame Number) to end(Frame Number).
    
    Input Parameters:-
    <video_loc>:-The Absolute Location of the Input Video
    <start>:-Starting Frame Number from which we will create the Output Video
    <end>:-End Frame Number till which we will create the Output Video
    <process_func>(Optional):-A Function which you want to apply on the Input Video Frames before Sending the Frame to the Output Video
    '''
    
    
    
    #print(f"Proceessing video for Frame Number {start} - {end}",flush=True)
    # Read video file
    video = cv2.VideoCapture(video_loc)
    # Extracting Video Name From the Video Location
    video_name = os.path.basename(video_loc).split(".")[0]
    

    # get height, width and fps of the video
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(round(video.get(cv2.CAP_PROP_FPS)))
    
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter()
    
    
    #Creating Name of File using its video name and then start and end number so it can be Further Used Properly
    output_video_loc = f"VD{video_name.lower()}__{start}__{end}.mp4"
    #lcoation of the Output Video will be the Current Working Directory
    
    
    out.open(output_video_loc, fourcc, fps, (width, height), True)


    video.set(cv2.CAP_PROP_POS_FRAMES,start-1)
    while start <= end:
        ret,frame = video.read()
        if ret == False:
            break                                            # Normal Exctraing Frames and Applying the Process Func if Passed
        else:                                                # And Then Creating the Output Video
            if process_func is not None:
                frame = process_func(frame,start)
            out.write(frame)
            start += 1
    video.release()
    out.release()
    
    
def combine_output_files(video_loc,output_video_loc):
    '''
    This Method Is Used to Concat the Multiple Video Files Created by the Indiviual Processes.
    It Will Create the Final Output Video that was Required.
    
    Input Parameters:-
    <video_loc>:-The Absolute Location of the Input Video
    <output_video_loc>:-The Output Video Location of the Final Video.
    '''
    
    
    
    output_video_loc = str(output_video_loc)
    
    
    def sort_it(x):
        x = x.split(".")[0]
        start = x.split("__")[1]
        start = int(start)
        return start
    
    #Extracting the VideoName Name From the Video Location
    video_name = os.path.basename(video_loc).split(".")[0]
    
    # Reading all the Multiple Video Files(Produced By Multiple Processes) Corresponding To the Input Video
    # Then Sorting It Accoridng To Start Number(Hence Arranging them in correct Order)
    list_of_output_files = sorted([fg for fg in os.listdir(os.getcwd()) if fg.split("__")[0] == f"VD{video_name.lower()}"],key=sort_it)
    
    # Creating a Temporary txt File and Storing all the Video Names We have to Merge in the Above Sorted Order
    txt_tmp_name = f"tmp_{video_name}.txt"
    with open(txt_tmp_name, "a") as f:
        for t in list_of_output_files:
            f.write("file {}\n".format(t))

    # use ffmpeg to combine the video output files
    ffmpeg_cmd = f"ffmpeg -y -loglevel error -f concat -safe 0 -i {txt_tmp_name} -vcodec copy " + output_video_loc
    sp.Popen(ffmpeg_cmd, shell=True).wait()

    # Remove the temperory txt and The Multiple Video Files Created by the Proceses
    for f in list_of_output_files:
        os.remove(f)
    os.remove(txt_tmp_name)
    
    
    
def process_And_Write_Videos(video_loc,output_video_loc,process_func=None,start=None,end=None):
    '''
    This the Main Method Which Creates the Output Video Using Multiprocessing.
    It Interanlly Uses the Two Above Method
    
    Input Parameters:-
    <video_loc>:-The Input Video's Absolute Location
    <output_video_loc>:-The Output Video's Location
    <process_func>(Optional):-The Function which we want to Apply on the Extracted Frames from the Input Video and then Send to the Output Video.
    <start>(Optional):-Starting Frame Number from which we will create the Output Video
    <end>(Optinal):-End Frame Number till which we will create the Output Video
    '''
    
    
    
    # Getting the Number of Cores of the CPU
    num_processes = mp.cpu_count()-2
    print(f"\nProcessing Video:- {video_loc} using {num_processes} processes...")
    
    
    start_time = time.monotonic()
    # Getting the Frame Count of the Input Video 
    cap = cv2.VideoCapture(video_loc)
    
    
    if start is not None and end is not None:
        
        
        frame_count = end - start
        
        
    else:
        
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        start = 1
        end = frame_count
          

    # Using MultiProcessing To Create Temproray Video Files By Different Process Using the Above Defined Function.
    buffer = int(frame_count // num_processes)
    #print(f"\n\nStart_Frame_Number = {start} \nEnd_Frame_Number = {end} \nFrame_Count = {frame_count}\nBuffer = {buffer}\n\n")
    
    prcs = []
    for i in range(num_processes - 1):
        ul = start
        ll = start + buffer - 1
        p = mp.Process(target=process_Video_for_Each_Process,args=(video_loc,ul,ll,process_func))
        prcs.append(p)
        p.start()
        start = ll + 1

    p = mp.Process(target=process_Video_for_Each_Process, args=[video_loc,start,end,process_func])
    prcs.append(p)
    p.start()
    [p.join() for p in prcs]
    
    # Combining the Multiple Video Files Using the Above Function
    combine_output_files(video_loc,output_video_loc)
    #print(f"Total Time Taken = {time.monotonic() - start_time}")
    
    
def writing_Frames_For_Timestamps(video_loc,start,end,output_data_dir):
    '''
    The Method Which will be used By Each Indivivual Thread
    It will Read and Write Frames from the Input Video from start(Frame Number) to end(Frame Number).
        
    Input Parameters:-
    <video_loc>:-The Absolute Location of the Input Video
    <start>:-Starting Frame Number from which we will create the Output Video
    <end>:-End Frame Number till which we will create the Output Video
    <>
    '''
    
    
    
    print(f"Writing Frames with Thread from :- {start} - {end}")
    
    
    # Using Normal OpenCV Code Reading The Video Frame by Frame and Storing Each Frame to The Disk
    video = cv2.VideoCapture(video_loc)
    #Setting the Current Positon Frame to Start-1 so that It Strat Extracting Frames from start
    video.set(cv2.CAP_PROP_POS_FRAMES,start-1)#Setting the Current Positon Frame to Start-1 so that It Strat Extracting Frames from start
    
    
    while start <= end:
        
        
        ret,frame = video.read()
        if ret == False:
            
            
            break
        else:
            
            
            image_loc = os.path.join(output_data_dir,f"FRAME_{start}.png")
            cv2.imwrite(image_loc,frame)
            start += 1
            
            
    video.release()



def process_And_Write_Frames(video_loc,start_frame_number,end_frame_number,OUTPUT_DATA_DIR,number_of_processes=20):

        
        start_time = time.monotonic()
        if not os.path.exists(OUTPUT_DATA_DIR):
            os.mkdir(OUTPUT_DATA_DIR)

        
        frame_count = end_frame_number - start_frame_number
        buffer = int(frame_count // number_of_processes)
        print(f"\n\nStart Frame Number={start_frame_number}\nEnd Frame Number={end_frame_number}\nFrame Count={frame_count}\nBuffer={buffer}")


        prcs = []
        start = start_frame_number
        for i in range(number_of_processes - 1):
            ul = start
            ll = start + buffer - 1
            p = threading.Thread(target=writing_Frames_For_Timestamps, args=[video_loc,ul, ll, OUTPUT_DATA_DIR])
            prcs.append(p)
            p.start()
            start = ll + 1


        p = threading.Thread(target=writing_Frames_For_Timestamps, args=[video_loc,start, end_frame_number, OUTPUT_DATA_DIR])
        prcs.append(p)
        p.start()


        [p.join() for p in prcs]


        print(f"Total Time Taken = {time.monotonic() - start_time}")