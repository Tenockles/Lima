#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#
# Lima compilation script
#
# Version 1.0
#
#
# Author: FL / AN (Hacked from S. Poirier)

from argparse import ArgumentParser
import multiprocessing as mp

import os
import sys
import shutil
import string
import time
import platform

copied_files = []

#------------------------------------------------------------------------------
# build exception
#------------------------------------------------------------------------------
class BuildError(Exception):
  pass

#------------------------------------------------------------------------------
# Project directory
#------------------------------------------------------------------------------
def set_project_dir(sub_dir):
  project_dir = os.path.join(current_dir, sub_dir)
  os.chdir(project_dir)

#------------------------------------------------------------------------------
# Copy files
#------------------------------------------------------------------------------
def copy_file_ext(from_path, to_path, file_ext):

  if not os.path.isdir(to_path):
    os.makedirs(to_path)

  files = os.listdir(from_path)
  for file in files:
    full_name = os.path.join(from_path, file)
    if os.path.isfile(full_name):
      root, ext = os.path.splitext(full_name)
      if ext == file_ext:
        shutil.copy(full_name, to_path)
        file_to_copy = file + ' copied in ' + to_path
        copied_files.append(file_to_copy)

#------------------------------------------------------------------------------
# Compilation
#------------------------------------------------------------------------------
def build(pom_file_options = ""):

  if not copyonly:
    print("Maven command = " + maven_clean_install + pom_file_options + maven_options)
    rc = os.system(maven_clean_install + pom_file_options + maven_options)
    if rc != 0:
        raise BuildError

#------------------------------------------------------------------------------
# Clean
#------------------------------------------------------------------------------
def clean():
  rc = os.system(maven_clean)
  if rc != 0:
    raise BuildError

#------------------------------------------------------------------------------
# Clean all modules
#------------------------------------------------------------------------------
def clean_all():
    print("Cleaning all\n")
    set_project_dir('.');clean()
    set_project_dir('third-party/Processlib');clean()
    for cam in camera_list:
        set_project_dir('camera/'+ cam);clean()
        if cam == "eiger":
            set_project_dir('camera/'+ cam +'/sdk/linux/EigerAPI');clean()
        if cam == "ufxc":
            set_project_dir('camera/'+ cam +'/UFXC-LIB/UFXCLib');clean()
    set_project_dir('applications/tango/cpp');clean()

#------------------------------------------------------------------------------
# build the LimaDetector device
#------------------------------------------------------------------------------
def build_device(target_path):
  print("Building Device LimaDetector\n'")
  set_project_dir('applications/tango/cpp')

  build(pom_file_options = maven_platform_options)

  if "linux" in sys.platform:
    if target_path is not None:
      dest_path = os.path.join(target_path, '')
      copy_file_ext(device_src_path, dest_path, '')
  if "win32" in sys.platform:
    if target_path is not None:
      dest_path = os.path.join(target_path, '')
      copy_file_ext(device_src_path, dest_path, '.exe')
      copy_file_ext(device_src_path, dest_path, '.pdb')

  print('\n')

#------------------------------------------------------------------------------
# build a module: either 'processlib', 'lima' (or 'core') or a camera plugin
#------------------------------------------------------------------------------
def build_module(module, target_path):

  """Build the selected module"""

  print("Building:    " + module + "\n")

  if module == "camera/eiger":
    # specific treatment for the EigerAPI library
    print("Building first:    " + module +'/sdk/linux/EigerAPI' + "\n")
    set_project_dir(module + '/sdk/linux/EigerAPI')	
    build(pom_file_options = maven_platform_options)
    # copy EigerAPI sdk
    if "linux" in sys.platform:
      if target_path is not None:
        dest_path = os.path.join(target_path, '')
        copy_file_ext(src_path, dest_path, '.so')	
        
  if module == "camera/ufxc":
    # specific treatment for the UFXCLib library
    print("Building first:    " + module +'/UFXC-LIB/UFXCLib' + "\n")
    set_project_dir(module+'/UFXC-LIB/UFXCLib')	
    build(pom_file_options = maven_platform_options)
    # copy UFXCLib sdk
    if "linux" in sys.platform:
      if target_path is not None:
        dest_path = os.path.join(target_path, '')
        copy_file_ext(src_path, dest_path, '.so')	
        
  # compil module
  set_project_dir(module)
  build(pom_file_options = maven_platform_options)

  # copy module if needed     
  if "linux" in sys.platform:
    if target_path is not None:
      dest_path = os.path.join(target_path, '')
      copy_file_ext(src_path, dest_path, '.so')
  if "win32" in sys.platform:
    if target_path is not None:
      dest_path = os.path.join(target_path, '')
      copy_file_ext(src_path, dest_path, '.dll')
      copy_file_ext(src_path, dest_path, '.pdb')

  print('\n')

#------------------------------------------------------------------------------
# build all cameras
#------------------------------------------------------------------------------
def build_all_camera(target_path):
    start=time.time()
    # this take 2 min 45 sec on a quad core
    if multi_proc == False:
        for cam in camera_list:
            build_module('camera/' + cam, target_path)
    else:
        
        """procs = []
        for cam in camera_list:
            proc = mp.Process(target=build_module, args=('camera/' + cam, target_path))
            procs.append(proc)
            proc.start()
        
        for proc in procs:
            proc.join()"""
    
        
        # this take 1 min 26 sec on a quad core
        """pool = mp.Pool(processes = mp.cpu_count())
        for cam in camera_list:
          print("multi proc: Building:    " + cam + "\n")
          
          pool.apply_async(build_module, ('camera/' + cam, target_path))
          time.sleep(2)
        
        pool.join()
        pool.close()

        time.strftime("%M min %S sec", time.localtime(170))"""

    print("duration for compiling all cameras (MultiProc = " + str(multi_proc) + ") = " + str(time.strftime("%M min %S sec", time.localtime(time.time() - start))))

#------------------------------------------------------------------------------
# Main Entry point
#------------------------------------------------------------------------------
if __name__ == "__main__":

  # Select the platform (linux/Win/32/64)
  if "linux" in sys.platform:
    if "i686" in platform.machine():
        platform                = "linux32"
        camera_list             = ["basler", "imxpad", "marccd","merlin", "pilatus","simulator", "xpad"]
        maven_platform_options  = " -Denv=linux_32"
        maven_clean             = "mvn clean"
        src_path                = './target/nar/lib/i386-Linux-g++/shared/'
        device_src_path         = './target/nar/bin/i386-Linux-g++/'
    elif "x86_64" in platform.machine():
        platform                = "linux64"
        camera_list             = ["eiger","slseiger","slsjungfrau","lambda","simulator", "xspress3", "ufxc","spectralinstrument"]
        maven_platform_options  = " --file pom_64.xml"
        maven_clean             = "mvn clean  --file pom_64.xml"
        src_path                = './target/nar/lib/i386-Linux-g++/shared/'
        device_src_path         = './target/nar/bin/i386-Linux-g++/'
  if "win32" in sys.platform:
    if "x86" in platform.machine():
        platform                = "win32"
        camera_list             = ["andor", "perkinelmer","roperscientific","simulator","uview"]
        maven_platform_options  = " -Denv=win_32_vc12"
        maven_clean             = "mvn clean"
        src_path                = './target/nar/lib/x86-Windows-msvc/shared/'
        device_src_path         = './target/nar/bin/x86-Windows-msvc/'
    else:
        platform                = "win64"
        camera_list             = ["dhyana","hamamatsu", "pco", "simulator", "spectrumone"]
        maven_platform_options  = " --file pom_64_Win7_shared.xml"
        maven_clean             = "mvn clean  --file pom_64_Win7_shared.xml"
        src_path                = './target/nar/lib/amd64-Windows-msvc/shared/'
        device_src_path         = './target/nar/bin/amd64-Windows-msvc/'

  print("=============================================")    
  print(" platform : " + platform)
  target_path = None

  # command line parsing
  parser = ArgumentParser(description="Lima compilation script")
  cams_string = ""
  for cam in camera_list:
    cams_string += cam + "|"
  help_string = "modules to compile (several modules are possible: all|processlib|lima|cameras|" + cams_string + "|device||cleanall)"
  parser.add_argument("modules",nargs = '*', help=help_string)
  parser.add_argument("-o","--offline", help="mvn will be offline",action="store_true")
  parser.add_argument("-f","--pomfile", help="name of the pom file(for the Tango device only)")
  parser.add_argument("-q","--quiet", help="mvn will be quiet", action="store_true")
  parser.add_argument("-m","--multiproc", help="cameras will be compiled in multiprocessing way",action="store_true")
  parser.add_argument("-d","--directory", help="automatically install Lima binaries into the specified installation directory")
  parser.add_argument("-c","--copyonlydir", help="only install Lima binaries into the specified installation directory")
  parser.add_argument("-e","--env", help="set the env option for the pom: eg: -e win_32_vc12 will set: -Denv=win_32_vc12 ;\
                                          it is also used to force linux32 on 64 bits linux: use -e linux_32")

  args = parser.parse_args()
  
  maven_options = ""
  # manage command line option  
  if args.offline:
    maven_options += " -o"

  if args.pomfile:
    maven_platform_options = " --file " + args.pomfile
    
  if args.env:
    maven_platform_options += " -Denv=" + args.env

  if args.quiet:
    maven_options += " -q"

  if args.multiproc:
    multi_proc = True
  else:
    multi_proc = False

  if args.directory:
    target_path = args.directory
  else:
    target_path = None
    
  if args.copyonlydir:
    target_path = args.copyonlydir
    copyonly = True
  else:
    copyonly = False
  
  
  # Force the platform to be linux32 even on 64 bits linux (this overload the platform selection from above)
  if args.env == 'linux_32':
    print(" Compilation " + args.env + " sur platform " + platform)
    platform                = "linux32"
    camera_list             = ["basler", "imxpad", "marccd","merlin", "pilatus","simulator", "xpad"]
    maven_platform_options  = " -Denv=linux_32"
    maven_clean             = "mvn clean"
    src_path                = './target/nar/lib/i386-Linux-g++/shared/'
    device_src_path         = './target/nar/bin/i386-Linux-g++/'  

  print("=============================================")  
  
  # variables
  maven_clean_install   = "mvn clean install -DenableCheckRelease=false"
  current_dir           = os.getcwd()
  
  for target in args.modules:
      try:
        # Build all
        if target == 'all':
            print('BUILD ALL\n')
            build_module('third-party/Processlib', target_path)
            build_module('.',target_path)
            build_all_camera(target_path)
            build_device(target_path)
        # Build processlib
        elif target == 'processlib':
            print('BUILD ProcessLib\n')
            build_module('third-party/Processlib', target_path)
        # Build lima
        elif target == 'lima' or target == 'core':
            print('BUILD Lima Core\n')
            build_module('.',target_path)
        # Build device
        elif target == 'device':
            print('BUILD Device\n')
            build_device(target_path)
        # Build cameras
        elif target == 'cameras':
            print('BUILD All ' + platform + ' Cameras\n')
            build_all_camera(target_path)
        # Clean all
        elif target =='cleanall':
            clean_all()
        # Build cam
        else:
            for cam in camera_list:
                if target == cam:
                    build_module('camera/'+cam, target_path)
                    break

        # display list of copied files, if -d or -c option is used
        if args.directory or args.copyonlydir:
            print('\n')
            print('=============================================')
            print('Modules are compiled & copied as shown below:')
            print('=============================================')
            for file in copied_files:
                print('- ' + file)
            print('\n')

      except BuildError as e:
        sys.stderr.write("!!!   BUILD FAILED    !!!\n")

