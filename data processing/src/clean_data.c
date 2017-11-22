#include <stdio.h>
#include <stdlib.h>
 
int main(int argc, char ** argv)
{
  char ch;
  FILE *fp;
  
  if (argc == 2)
    fp = fopen(argv[1],"r"); // read mode
  else {
    fp = stdin; 
    /* fprintf(stderr,"usage: ./clean_file FILE\n"); */
    /* exit(-1); */
  }
  
  
  if( fp == NULL )
    {
      perror("Error while opening the file");
      exit(EXIT_FAILURE);
    }
  
  while( ( ch = fgetc(fp) ) != EOF){
    if(ch>0) printf("%c",ch);
  }
  printf("\n");
  
  fclose(fp);
  return 0;
}
