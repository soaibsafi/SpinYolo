import os
import PySpin
import sys
import time

import yolo_detect

ACQ_MODE = 1

WIDTH = 1024
HEIGHT = 768
BINNING = 2
FORMAT = 'BGR8'
ACQUITION_MODE = 'Continuous'
H_BINNINGMODE = 'Average'
V_BINNINGMODE = 'Average'
STREAM_DEFAULT_BUFFER_COUNT = 3
STREAM_DEFAULT_BUFFER_COUNT_MODE = 'Manual'
STREAM_BUFFER_COUNT_MODE = 'Manual'
STREAM_BUFFER_HANDLING_MODE = 'NewestOnly'
TRIGGER_SOURCE = 'Software'
TFIGGER_MODE = 'Off'

# Reset camera setting
def ResetCameraSetting(nodemap):
    print('*** RESET CAMERA SETTING ***')

    result = True

    node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode('OffsetX'))
    node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode('OffsetY'))
    node_binning_h = PySpin.CIntegerPtr(
        nodemap.GetNode('BinningHorizontal'))
    node_binning_v = PySpin.CIntegerPtr(nodemap.GetNode('BinningVertical'))

    try:
        print('--- Reseting configuration parameter---')

        # Ensuring trigger mode is off
        if PySpin.IsAvailable(node_trigger_mode) and PySpin.IsWritable(node_trigger_mode):
            node_trigger_mode_to_set = node_trigger_mode.GetEntryByName('Off')

            if PySpin.IsAvailable(node_trigger_mode_to_set) and PySpin.IsReadable(node_trigger_mode_to_set):
                trigger_mode_to_set = node_trigger_mode_to_set.GetValue()
                node_trigger_mode.SetIntValue(trigger_mode_to_set)
            else:
                print(
                    '!!!Trigger mode is ON (Should be turned off before configuring the device)')

        else:
            print('Triger Mode: ')
            if not PySpin.IsAvailable(node_trigger_mode):
                print('Not available')
            elif not PySpin.IsWritable(node_trigger_mode):
                print('Not Writable')

        # Strat reseting values

        # Apply minimum to offset X
        if PySpin.IsAvailable(node_offset_x) and PySpin.IsWritable(node_offset_x):
            node_offset_x.SetValue(node_offset_x.GetMin())
            print('Offset X set to %i...' % node_offset_x.GetMin())
        else:
            print('Offset X not available...')

         # Apply minimum to offset Y
        if PySpin.IsWritable(node_offset_y) and PySpin.IsWritable(node_offset_y):
            node_offset_y.SetValue(node_offset_y.GetMin())
            print('Offset Y set to %i...' % node_offset_y.GetMin())
        else:
            print('Offset Y not available...')

        # Set Horizontal Binning
        if PySpin.IsAvailable(node_binning_h) and PySpin.IsWritable(node_binning_h):
            node_binning_h.SetValue(1)
            print('Binning Horizontal set to 1.')
        else:
            print('Binning Horizontal is not available.')

        # Set Vertical Binning
        if PySpin.IsAvailable(node_binning_v) and PySpin.IsWritable(node_binning_v):
            node_binning_v.SetValue(1)
            print('Binning Vertical set to 1')
        else:
            print('Binning Vertical is not available')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

# Configure Image Format
def ConfigureCameraSetting(nodemap):
    print('*** CONFIGURING CAMERA ***')

    result = True

    node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))
    node_acquisition_mode = PySpin.CEnumerationPtr(
        nodemap.GetNode('AcquisitionMode'))
    node_offset_x = PySpin.CIntegerPtr(nodemap.GetNode('OffsetX'))
    node_offset_y = PySpin.CIntegerPtr(nodemap.GetNode('OffsetY'))
    node_width = PySpin.CIntegerPtr(nodemap.GetNode('Width'))
    node_height = PySpin.CIntegerPtr(nodemap.GetNode('Height'))

    node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    node_binning_selector = PySpin.CEnumerationPtr(
        nodemap.GetNode('BinningSelector'))
    node_binning_H_mode = PySpin.CEnumerationPtr(
        nodemap.GetNode('BinningHorizontalMode'))
    node_binning_V_mode = PySpin.CEnumerationPtr(
        nodemap.GetNode('BinningVerticalMode'))
    node_binning_h = PySpin.CIntegerPtr(nodemap.GetNode('BinningHorizontal'))
    node_binning_v = PySpin.CIntegerPtr(nodemap.GetNode('BinningVertical'))

    # Set Image Format
    maxX = node_width.GetMax()
    maxY = node_height.GetMax()
    print('--------MAxX: %s'%maxX)
    print('--------MAxY: %s'%maxY)

    tempX = (maxX - WIDTH * BINNING)
    tempY = (maxY - HEIGHT * BINNING)
    print('--------tempX: %s'%tempX)
    print('--------tempY: %s'%tempY)

    if tempX < 0:
        OffSetX = 0
    if tempY < 0:
        OffSetY = 0

    OffSetY = (tempY / (BINNING*2))
    OffSetX = (tempX / (BINNING * 2))
    OffSetX = (OffSetX - (OffSetX % 4))
    OffSetY = (OffSetY - (OffSetY % 4))
    print('--------OffsetX: %s'%OffSetX)
    print('--------OffSetY: %s'%OffSetY)

    try:
        # Set Acquisition Mode
        if PySpin.IsAvailable(node_acquisition_mode) and PySpin.IsWritable(node_acquisition_mode):
            node_acquisition_mode_to_set = node_acquisition_mode.GetEntryByName(
                ACQUITION_MODE)

            if PySpin.IsAvailable(node_acquisition_mode_to_set) and PySpin.IsReadable(node_acquisition_mode_to_set):

                print('--- Acquisition Mode: %s' %
                      node_acquisition_mode.GetCurrentEntry().GetSymbolic(), end='')
                acquisition_mode = node_acquisition_mode_to_set.GetValue()
                node_acquisition_mode.SetIntValue(acquisition_mode)
                print('-> %s' %
                      node_acquisition_mode.GetCurrentEntry().GetSymbolic())
            else:
                print('Acquisition Mode [%s] is ' % ACQUITION_MODE, end='')
                if not PySpin.IsAvailable(node_acquisition_mode_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_acquisition_mode_to_set):
                    print('not Readable')
        else:
            print('!!! Acquisition: ', end='')
            if not PySpin.IsAvailable(node_acquisition_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_acquisition_mode):
                print('not Writable')

        # Apply pixel format
        if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):
            node_pixel_format_to_set = node_pixel_format.GetEntryByName(FORMAT)

            if PySpin.IsAvailable(node_pixel_format_to_set) and PySpin.IsReadable(node_pixel_format_to_set):
                print('--- Pixel Format: %s' %
                      node_pixel_format.GetCurrentEntry().GetSymbolic(), end='')
                pixel_format_to_set = node_pixel_format_to_set.GetValue()
                node_pixel_format.SetIntValue(pixel_format_to_set)
                print('-> %s' % node_pixel_format.GetCurrentEntry().GetSymbolic())
            else:
                print('Pixel Format [%s] is ' % FORMAT, end='')
                if not PySpin.IsAvailable(node_pixel_format_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_pixel_format_to_set):
                    print('not Readable')
                else:
                    print()
        else:
                print('Pixel Format: ', end='')
                if not PySpin.IsAvailable(node_pixel_format):
                    print('not Available')
                elif not PySpin.IsWritable(node_pixel_format):
                    print('not Readable')
                else:
                    print()

        # Apply pixel binning horizontal
        if PySpin.IsAvailable(node_binning_H_mode) and PySpin.IsWritable(node_binning_H_mode):
            node_binning_H_mode_to_set = node_binning_H_mode.GetEntryByName(
                H_BINNINGMODE)
            if PySpin.IsAvailable(node_binning_H_mode_to_set) and PySpin.IsReadable(node_binning_H_mode_to_set):
                print('--- H. Binning Mode: %s' %
                      node_binning_H_mode.GetCurrentEntry().GetSymbolic(), end='')
                binning_h_mode_to_set = node_binning_H_mode_to_set.GetValue()
                node_binning_H_mode.SetIntValue(binning_h_mode_to_set)
                print('-> %s.' %
                      node_binning_H_mode.GetCurrentEntry().GetSymbolic())
            else:
                print('!!! H. Binning Mode: [%s] is ' % H_BINNINGMODE, end='')
                if not PySpin.IsAvailable(node_binning_H_mode_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_binning_H_mode_to_set):
                    print('not Readable')
                else:
                    print()
        else:
            print('!!! H. Binning Mode: ', end='')
            if not PySpin.IsAvailable(node_binning_H_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_binning_H_mode):
                print('not Writable')
            else:
                print()

         # Apply pixel binning vertical
        if PySpin.IsAvailable(node_binning_V_mode) and PySpin.IsWritable(node_binning_V_mode):
            node_binning_V_mode_to_set = node_binning_V_mode.GetEntryByName(
                V_BINNINGMODE)
            if PySpin.IsAvailable(node_binning_V_mode_to_set) and PySpin.IsReadable(node_binning_V_mode_to_set):
                print('--- V. Binning Mode: %s' %
                      node_binning_V_mode.GetCurrentEntry().GetSymbolic(), end='')
                binning_v_mode_to_set = node_binning_V_mode_to_set.GetValue()
                node_binning_V_mode.SetIntValue(binning_v_mode_to_set)
                print('-> %s.' %
                      node_binning_V_mode.GetCurrentEntry().GetSymbolic())
            else:
                print('!!! V. Binning Mode: [%s] is ' % V_BINNINGMODE, end='')
                if not PySpin.IsAvailable(node_binning_V_mode_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_binning_V_mode_to_set):
                    print('not Readable')
                else:
                    print()
        else:
            print('!!! V. Binning Mode: ', end='')
            if not PySpin.IsAvailable(node_binning_V_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_binning_V_mode):
                print('not Writable')
            else:
                print()

        # Set Binning H value
        if PySpin.IsAvailable(node_binning_h) and PySpin.IsWritable(node_binning_h):
            print('--- Binning H: %s' % node_binning_h.GetValue(), end='')
            node_binning_h.SetValue(BINNING)
            print('-> %s' % node_binning_h.GetValue())
        else:
            print('!!! Binning H: ', end='')
            if not PySpin.IsAvailable(node_binning_h):
                print('not Available')
            elif not PySpin.IsWritable(node_binning_h):
                print('not Writable')
            else:
                print()

        # Set Binning V value
        if PySpin.IsAvailable(node_binning_v) and PySpin.IsWritable(node_binning_v):
            print('--- Binning V: %s' % node_binning_v.GetValue(), end='')
            node_binning_v.SetValue(BINNING)
            print('-> %s' % node_binning_v.GetValue())
        else:
            print('!!! Binning V: ', end='')
            if not PySpin.IsAvailable(node_binning_v):
                print('not Available')
            elif not PySpin.IsWritable(node_binning_v):
                print('not Writable')
            else:
                print()

        # Set Width Value
        if PySpin.IsAvailable(node_width) and PySpin.IsWritable(node_width):
            print('--- Width: %s' % node_width.GetValue(), end='')
            node_width.SetValue(WIDTH)
            print('-> %s' % node_width.GetValue())
        else:
            print('!!! Width: ', end='')
            if not PySpin.IsAvailable(node_width):
                print('not Available')
            elif not PySpin.IsWritable(node_width):
                print('not Writable')
            else:
                print()

        # Set Height Value
        if PySpin.IsAvailable(node_height) and PySpin.IsWritable(node_height):
            print('--- Height: %s' % node_height.GetValue(), end='')
            node_height.SetValue(HEIGHT)
            print('-> %s' % node_height.GetValue())
        else:
            print('!!! Height: ', end='')
            if not PySpin.IsAvailable(node_height):
                print('not Available')
            elif not PySpin.IsWritable(node_height):
                print('not Writable')
            else:
                print()

        # Set offset X value
        if PySpin.IsAvailable(node_offset_x) and PySpin.IsWritable(node_offset_x):
            print('--- Offset X: %s' % node_offset_x.GetValue(), end='')
            node_offset_x.SetValue(int(OffSetX))
            print('-> %s' % node_offset_x.GetValue())
        else:
            print('!!! OffsetX: ', end='')
            if not PySpin.IsAvailable(node_offset_x):
                print('not Available')
            elif not PySpin.IsWritable(node_offset_x):
                print('not Writable')
            else:
                print()

        # Set offset X value
        if PySpin.IsAvailable(node_offset_y) and PySpin.IsWritable(node_offset_y):
            print('--- Offset X: %s' % node_offset_y.GetValue(), end='')
            node_offset_y.SetValue(int(OffSetY))
            print('-> %s' % node_offset_y.GetValue())
        else:
            print('!!! OffsetY: ', end='')
            if not PySpin.IsAvailable(node_offset_y):
                print('not Available')
            elif not PySpin.IsWritable(node_offset_y):
                print('not Writable')
            else:
                print()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

# Buffer Handling
def ConfigureStreamSetting(nodemap):
    print('=== CONFIGURE STREAM ===')

    result = True

    try:
        node_default_count_mode = PySpin.CEnumerationPtr(
            nodemap.GetNode('StreamDefaultBufferCountMode'))
        #print('------------StreamDefaultBufferCountMode: %s'%PySpin.IsAvailable(node_default_count_mode))
        node_count_mode = PySpin.CEnumerationPtr(
            nodemap.GetNode('StreamBufferCountMode'))
        node_count = PySpin.CIntegerPtr(
            nodemap.GetNode('StreamDefaultBufferCount'))
        node_handling_mode = PySpin.CEnumerationPtr(
            nodemap.GetNode('StreamBufferHandlingMode'))

        # Set Stream buffer handling mode
        if PySpin.IsAvailable(node_handling_mode) and PySpin.IsWritable(node_handling_mode):
            node_handling_mode_to_set = node_handling_mode.GetEntryByName(
                STREAM_BUFFER_HANDLING_MODE)
            if PySpin.IsAvailable(node_handling_mode_to_set) and PySpin.IsReadable(node_handling_mode_to_set):
                print('--- Stream Buffer Handling Mode: %s' %
                      node_handling_mode.GetCurrentEntry().GetSymbolic(), end='')
                handling_mode_to_set = node_handling_mode_to_set.GetValue()
                node_handling_mode.SetIntValue(handling_mode_to_set)
                print('-> %s' % node_handling_mode.GetCurrentEntry().GetSymbolic())
            else:
                print(
                    '!!!Stream Buffer Handling Mode [%s] is' % STREAM_BUFFER_HANDLING_MODE, end='')
                if not PySpin.IsAvailable(node_handling_mode_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_handling_mode_to_set):
                    print('not Readable')
                else:
                    print()
        else:
            print('!!! Stream Buffer Handling Mode: ', end='')
            if not PySpin.IsAvailable(node_handling_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_handling_mode):
                print('not Writable')
            else:
                print()

        # Set Strem Default Buffer count mode
        if PySpin.IsAvailable(node_default_count_mode) and PySpin.IsWritable(node_default_count_mode):
            node_default_count_mode_to_set = node_default_count_mode.GetEntryByName(
                STREAM_DEFAULT_BUFFER_COUNT_MODE)
           
            if PySpin.IsAvailable(node_default_count_mode_to_set) and PySpin.IsReadable(node_default_count_mode_to_set):
                print('--- Stream Default Buffer Count Mode: %s' %
                      node_default_count_mode.GetCurrentEntry().GetSymbolic(), end='')
                default_count_mode_to_set = node_default_count_mode_to_set.GetValue()
                node_default_count_mode.SetIntValue(default_count_mode_to_set)
                print('-> %s' %
                      node_default_count_mode.GetCurrentEntry().GetSymbolic())
            else:
                print(
                    '!!!StreamDefaultBufferCountMode: [%s] is ' % STREAM_DEFAULT_BUFFER_COUNT_MODE, end='')
                if not PySpin.IsAvailable(node_default_count_mode_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_default_count_mode_to_set):
                    print('not Reabable')
                else:
                    print()
        else:
            print('!!! StreamDefaultBufferCountMode: ', end='')
            if not PySpin.IsAvailable(node_default_count_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_default_count_mode):
                print('not Writable')
            else:
                print()

        # set Stream Buffer Count Mode
        if PySpin.IsAvailable(node_count_mode) and PySpin.IsWritable(node_count_mode):
            node_count_mode_to_set = node_count_mode.GetEntryByName(
                STREAM_BUFFER_COUNT_MODE)
            if PySpin.IsAvailable(node_count_mode_to_set) and PySpin.IsReadable(node_count_mode_to_set):
                print('--- StreamBufferCountMode: %s' %
                      node_count_mode.GetCurrentEntry().GetSymbolic(), end='')
                count_mode_to_set = node_count_mode_to_set.GetValue()
                print('-> %s' % node_count_mode.GetCurrentEntry().GetSymbolic())
            else:
                print('!!!StreamBufferCountMode: [%s] is ' %
                      STREAM_BUFFER_COUNT_MODE, end='')
                if not PySpin.IsAvailable(node_count_mode_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_count_mode_to_set):
                    print('not Readable')
                else:
                    print()
        else:
            print('!!!StreamBufferCountMode: ', end='')
            if not PySpin.IsAvailable(node_count_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_count_mode):
                print('not Writable')
            else:
                print()

        # Set StreamDefaultBufferCount
        if PySpin.IsAvailable(node_count) and PySpin.IsWritable(node_count):
            print('--- StreamDefaultBufferCount: %s' %
                  node_count.GetValue(), end='')
            node_count.SetValue(STREAM_DEFAULT_BUFFER_COUNT)
            print('-> %s' % node_count.GetValue())
        else:
            print('!!! StreamDefaultBufferCount: ', end='')
            if not PySpin.IsAvailable(node_count):
                print('not Available')
            elif not PySpin.IsWritable(node_count):
                print('not Writable')
            else:
                print()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

# Pring device information
def PrintDeviceInfo(nodemap):
    result = True

    print('=== PRINTING DEVICE INFORMATION ===')

    try:
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))
        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(), node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result

# Configure Trigger for software Information
def ConfigureTrigger(cam, nodemap):
    print('*** COCNFIGURING TRIGGER ***')

    result = True

    node_trigger_source = PySpin.CEnumerationPtr(
        nodemap.GetNode('TriggerSource'))
    node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))

    try:
        # Ensure Trigger mode is off
        if PySpin.IsAvailable(node_trigger_mode) and PySpin.IsWritable(node_trigger_mode):
            node_trigger_mode_to_set = node_trigger_mode.GetEntryByName('Off')
            if PySpin.IsAvailable(node_trigger_mode_to_set) and PySpin.IsReadable(node_trigger_mode_to_set):
                print('--- Trigger Mode: %s' % node_trigger_mode.GetCurrentEntry().GetSymbolic(), end='')
                trigger_mode_to_set = node_trigger_mode_to_set.GetValue()
                node_trigger_mode.SetIntValue(trigger_mode_to_set)
                print('-> %s' % node_trigger_mode.GetCurrentEntry().GetSymbolic())
            else:
                print('!!! Trigger Mode: [Off] is', end='')
                if not PySpin.IsAvailable(node_trigger_mode_to_set):
                    print('not available')
                elif PySpin.IsReadable(node_trigger_mode_to_set):
                    print('not Readable')
                else:
                    print()
        else:
            print('!!!Trigger Mode: ', end='')
            if not PySpin.IsAvailable(node_trigger_mode):
                print('not Available')
            elif not PySpin.IsWritable(node_trigger_mode):
                print('not Writable')
            else:
                print()

        # Set Trigger Mode
        if PySpin.IsAvailable(node_trigger_source) and PySpin.IsWritable(node_trigger_source):
            node_trigger_source_to_set = node_trigger_source.GetEntryByName(
                TRIGGER_SOURCE)
            if PySpin.IsAvailable(node_trigger_source_to_set) and PySpin.IsReadable(node_trigger_source_to_set):
                print('--- Trigger Source: %s' %
                      node_trigger_source.GetCurrentEntry().GetSymbolic(), end='')
                trigger_source_to_set = node_trigger_source_to_set.GetValue()
                node_trigger_source.SetIntValue(trigger_source_to_set)
                print('-> %s' %
                      node_trigger_source.GetCurrentEntry().GetSymbolic())
            else:
                print('!!! Trigger Source: [%s] is ' % TRIGGER_SOURCE, end='')
                if not PySpin.IsAvailable(node_trigger_source_to_set):
                    print('not Available')
                elif not PySpin.IsReadable(node_trigger_source_to_set):
                    print('not Readable')
                else:
                    print()
        else:
            print('!!! Trigger Source: ', end='')
            if not PySpin.IsAvailable(node_trigger_source):
                print('not Available')
            elif not PySpin.IsWritable(node_trigger_source):
                print('not Writable')
            else:
                print()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        cam.EndAcquisition()
        return False

    return result


# Read Image
def AcquireImage(cam, nodemap):
    device_serial_number = ''
    node_device_serial_number = PySpin.CStringPtr(
        nodemap.GetNode('DeviceSerialNumber'))
    if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
        device_serial_number = node_device_serial_number.GetValue()
    
    result_image = cam.GetNextImage()
    if result_image.IsIncomplete():
        print('Image incomplete with image status %d ...' %result_image.GetImageStatus())
    else:
        width = result_image.GetWidth()
        height = result_image.GetHeight()
        #print('Grabbed Image with width u= %d, height = %d' %(width, height))

    #if not ACQ_MODE:  # 0: Image
        #image_converted = result_image.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
        # Create a unique filename
        #if device_serial_number:
        #    filename = 'Acquisition-%s-%dx%d-b-%d.jpg' % (device_serial_number, WIDTH, HEIGHT, BINNING)
        #else:  # if serial number is empty
        #    filename = 'Acquisition-%dx%d-b-%d.jpg' % (WIDTH, HEIGHT, BINNING)

        # Save image
        #image_converted.Save(filename)
        #print('Image saved at %s' % filename)
    
    # print('Xpadding: %s'%result_image.GetXPadding())
    # print('Ypadding: %s'%result_image.GetYPadding())
    # print('Stride: %s'%result_image.GetStride())
    # print('Colsize: %s'%result_image.GetHeight())
    # print('RowSize: %s'%result_image.GetWidth())

    print('')

    return result_image

"""
#image_data = pImage.GetNDArray()
    #plt.imshow(image_data)
    #plt.pause(0.00001)
    #plt.clf()
    #print('Printing Image')
"""
import cv2
# Display Image/video
def DisplayCamera(pImage):
    image_data = pImage.GetNDArray()
    cv2.namedWindow('Frame', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Frame', image_data)
 

# Run For single camera
def RunSingleCamera(cam):
    result = True
    err = True

    try:
        cam.Init()
        nodemap_tldevice = cam.GetTLDeviceNodeMap()
        #result &= PrintDeviceInfo(nodemap_tldevice)

        nodemap_tlstream = cam.GetTLStreamNodeMap()
        #result &= PrintDeviceInfo(nodemap_tlstream)

        nodemap = cam.GetNodeMap()

        err &= ResetCameraSetting(nodemap)
        err &=ConfigureStreamSetting(nodemap_tlstream)
        err &= ConfigureCameraSetting(nodemap)
        err &= ConfigureTrigger(cam, nodemap)

        if not err:
            return err
        
        # Begin Acquiring Images
        print('*** ACQUIRING & DISPLAY IMAGE ***')
        print('!!!Press Esc to exit properly.')

        cam.BeginAcquisition()

        if ACQ_MODE == 0:
            start_time = time.time()
            image = AcquireImage(cam, nodemap)
            end_time = time.time()
            frame = DisplayCamera(image)
            image.Release()
            required_time = end_time-start_time
            #fps = 1/required_time
            print('FPS: %s'%(1/required_time))
            while(True):
                if cv2.waitKey(30) &0xFF == 27:
                    print('Program is closing...')
                    break
        else:
            start_time = 0
            end_time = 0
            while(True):
                previous_time = start_time
                previous_end_time = end_time
                start_time = time.time()
                pImage = AcquireImage(cam, nodemap)
                #TODO Set input to the model
                yolo_detect.detect(pImage)
                end_time = time.time()
                #DisplayCamera(pImage)
                pImage.Release()
               
                required_time = previous_end_time-previous_time
                required_time2 = start_time-previous_time
                #fps = 1/required_time
                
                #print('Required Time: %s'%(required_time*1000))
                print('Difference: %s'%((required_time2-required_time)*1000))
                #print('Iteration Time: %s'%(required_time2*1000))
                
                #print('FPS: %s'%(1/required_time2))
                
                if cv2.waitKey(1) &0xFF == 27:
                    print('Program is closing...')
                    break
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        cam.EndAcquisition()
        return False
        
    cam.EndAcquisition()
    cam.DeInit()
            

def main():
    result = True
    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()
    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()
    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('!!!Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    for i, cam in enumerate(cam_list):
        print('Running example for camera %d...' % i)
        result &= RunSingleCamera(cam)
        print('Camera %d example complete... \n' % i)
    
    del cam
    # Clear camera list before releasing system
    cam_list.Clear()
    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result



if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
