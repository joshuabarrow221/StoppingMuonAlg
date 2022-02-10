#include <cstdlib>
#include <cstdio>
#include <iostream>
#include <fstream>

using namespace std;

//Run through the file and make many cut files
void hexdump_file_cut(string inFile_data = "")
{
  //Make some global variables
  string hexdump_original_filename = /*"seb01_28552"*/inFile_data;//Example file name
  std::cout << hexdump_original_filename << std::endl;
  
  string start_of_frame = "FFFFFFFF";//Start frame word
  string end_of_frame = "E0000000";//End of frame word
  string crap = "  CRAPCRAP  ";
  int number_lines_original_file = 0;
  //std::cout << number_lines_original_file << std::endl;
  int max_number_of_frames = 500;//Maximum number of frames we want in each cut file
  //Make strings to read from
  string first_number, column1, column2, column3, column4, column5, column6, column7, column8;
  int number_of_frames = 0;//Initialize counter for when the end of a frame is found
  std::ifstream in_hexdump_file_original;
  in_hexdump_file_original.open(hexdump_original_filename);//Create stream to read in hexadecimal file
  std::string line;
  while (std::getline(in_hexdump_file_original, line))
    {
      number_lines_original_file++;
      //in_hexdump_file_original >> column1 >> column2 >> column3 >> column4 >> column5 >> column6 >> column7 >> column8;
      //cout << first_number << "  " << column2 << "  " << column3 << "  " << column4 << "  " << column5 << "  " << column6 << "  " <<  column7 << "  " << column8 << std::endl;
    }
  //std::cout << number_lines_original_file << std::endl;
  //in_hexdump_file_original.seekg (0, ios::beg);
  in_hexdump_file_original.close();
  in_hexdump_file_original.open(hexdump_original_filename);
  
  //Read in the file's first line
  in_hexdump_file_original >> first_number >> column2 >> column3 >> column4 >> column5 >> column6 >> column7 >> column8;

  //Create an out stream filename
  string out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_0");
  std::cout << out_cut_hexdump_filename << std::endl;
  
  //Create the new cut file stream
  std::ofstream out_cut_hexdump_file;
  //Output the new filelist stream
  std::ofstream filelist;
  //Open the cut file
  out_cut_hexdump_file.open(out_cut_hexdump_filename);
  filelist.open("filelist.txt");
  //Write out the first line of the hexdump
  out_cut_hexdump_file << first_number << "  " << column2 << "  " << column3 << "  " << column4 << "  " << column5 << "  " << column6 << "  " <<  column7
		       << "  " << column8 << std::endl;
  //Write out the file name/path
  filelist << out_cut_hexdump_filename << std::endl;

  for(int i=1; i < number_lines_original_file; i++)
    {
      in_hexdump_file_original >> column1 >> column2 >> column3 >> column4 >> column5 >> column6 >> column7 >> column8;
      
      out_cut_hexdump_file << column1 << "  ";
      if ( column1 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 1: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  ";
	    }
	}
      out_cut_hexdump_file << column2 << "  ";
      if ( column2 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 2: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  CRAPCRAP  ";
	    }
	} 
      out_cut_hexdump_file << column3 << "  ";
      if ( column3 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 3: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  CRAPCRAP  CRAPCRAP  ";
	    }
	}
      out_cut_hexdump_file << column4 << "  ";
      if ( column4 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 4: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  CRAPCRAP  CRAPCRAP  CRAPCRAP  ";
	    }
	}
      out_cut_hexdump_file << column5 << "  ";
      if ( column5 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 5: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  CRAPCRAP  CRAPCRAP  CRAPCRAP  CRAPCRAP  ";
	    }
	}
      out_cut_hexdump_file << column6 << "  ";
      if ( column6 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 6: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
              filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  CRAPCRAP  CRAPCRAP  CRAPCRAP  CRAPCRAP  CRAPCRAP  ";
	    }
	}
      out_cut_hexdump_file << column7 << "  ";
      if ( column7 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 7: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      out_cut_hexdump_file << first_number << "  CRAPCRAP  CRAPCRAP  CRAPCRAP  CRAPCRAP  CRAPCRAP  CRAPCRAP  ";
	    }
	}
      out_cut_hexdump_file << column8 << std::endl;
      if ( column8 == end_of_frame )
	{
	  number_of_frames++;
	  //std::cout << "Column 8: " << number_of_frames << "  " << i << std::endl;
	  if( (number_of_frames % max_number_of_frames) == 0)
	    {
	      out_cut_hexdump_file.close();
	      out_cut_hexdump_filename.clear();
	      hexdump_original_filename.clear();
	      hexdump_original_filename = inFile_data/*"seb01_28552"*/;
	      out_cut_hexdump_filename = hexdump_original_filename.append("_subrun_");
	      out_cut_hexdump_filename.append( to_string(number_of_frames/max_number_of_frames) );
	      out_cut_hexdump_file.open(out_cut_hexdump_filename);
	      std::cout << out_cut_hexdump_filename << std::endl;
	      filelist << out_cut_hexdump_filename << std::endl;
	      //out_cut_hexdump_file << first_number << "  ";
	    }
	}      
    }
  filelist.close();
}
