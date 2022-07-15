#include <stdlib.h>
#include <windows.h>
#include <stdio.h>

#include "JpegFile.h"

void main ()
{
	if (__argc < 2 )
	{
		printf ( "thumb infile outfile width height") ;
		return ;
	}

	UINT nNewWidth, nNewHeight, nScale=1;

	if ( __argc < 4 )
		nNewWidth = 100 ;
	else
		nNewWidth = atoi(__argv[3]) ;

	if ( __argc < 5 )
		nNewHeight = 80 ;
	else
		nNewHeight = atoi(__argv[4]) ;

	JpegFile jFile ;
	unsigned int nWidth, nHeight ;
	char szOutFile[128] ;
	if ( __argc == 2 )
	{
		char *ptr = strrchr(__argv[1], '\\') ;
		if ( ptr )
		{
			*ptr = 0 ;
			sprintf ( szOutFile, "%s\\th%s",__argv[1],ptr+1) ;
			*ptr = '\\' ;
		}
		else
			sprintf ( szOutFile, "th%s",__argv[1]) ;
	}
	else
		sprintf ( szOutFile, "%s",__argv[2]) ;

	BYTE *pBuff = jFile.JpegFileToRGB ( __argv[1], &nWidth, &nHeight ) ;
	if ( pBuff )
	{
		while ( nWidth / nScale > nNewWidth )
			nScale ++ ;
		while ( nHeight / nScale > nNewHeight )
			nScale ++ ;

		if (jFile.RGBToJpegFile (szOutFile, pBuff, nWidth, nHeight, TRUE, 75 ) ==FALSE)
			printf ("Error writing file %s\n", szOutFile);
	}
	else
		printf ("Error reading file %s\n", __argv[1]);


}


