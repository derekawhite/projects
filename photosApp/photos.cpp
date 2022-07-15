#include <stdio.h>
#include <stdlib.h>
#include <search.h>
#include <string.h>
#include <direct.h>
#include <windows.h>
#include <time.h>
#include "jpegfile.h"
#include "EXIF.h"

#pragma warning (disable : 4996)

#define FAV_THUMB_WIDTH  128
#define FAV_THUMB_HEIGHT 96
#define FAV_WIDTH  800
unsigned int nImgHeight = 600;
#define MIN_SIZE 1024*10

//#define ThumbsFolderSlash "../../../thumbs/"
//#define ThumbsFolderBackslash "..\\..\\..\\thumbs\\"

#define ThumbsFolderSlash "../thumbs/"
#define ThumbsFolderBackslash "..\\thumbs\\"

int nThumbHeight = 90;
int nThumbWidth = 120;
bool bAllowNegatives = TRUE;
int nCols = 7;
int nBig = 40;
int nSmall = 20;
int nCCols = 4;
int nCRows = 3;
int nTop = 3;
BOOL bCopy = FALSE;
BOOL bAPAY = FALSE;
BOOL bSlideshow = FALSE;
BOOL bDoIndex = FALSE;
BOOL bStartIndex = FALSE;
BOOL bEndIndex = FALSE;
BOOL bDoSortByTitle = FALSE;
BOOL bSortByTime = FALSE;
BOOL bDoNegatives = FALSE;
BOOL bDoMore = FALSE;
BOOL bDoFavourites = FALSE;
BOOL bRenameSort = FALSE;
BOOL bTaken = TRUE;
BOOL bMinutes = FALSE;
BOOL bDoDate = TRUE;
BOOL bLes = FALSE;

char *rsName = NULL;

BOOL bReverse = FALSE;
BOOL bNoMissing = TRUE;
BOOL bThumb = FALSE;
BOOL bSmooth = TRUE;
BOOL bCrunch = FALSE;
BOOL bPixellate = FALSE;
BOOL bUnique = FALSE;
BOOL bScanTooSmall = FALSE;
BOOL bAuto = FALSE;
BOOL bGaps = FALSE;
BOOL bList = FALSE;
BOOL bExif = FALSE;
BOOL bOrientation = FALSE;
int  nQuality = 90;
int  nFiles = 0;
BOOL bDoSkip = TRUE;

#define TITLE_LEN 1280

char szFolder[256] = { 0 };
char szGlobalTitle[TITLE_LEN] = "";
char szGlobalShortTitle[TITLE_LEN] = "";
int  nTitles = 0;
char *pNext = NULL;
char *pPrev = NULL;
char *szTitlesFile = NULL;
char *szShortFile = NULL;
char *szFull = NULL;
char *szMissing = "";
char *szBlank = "";
char *szDuplicate = "";
char *szPixelFile = NULL;
char *szCrunchFile = "crunch.bin";
char szMinTaken[20] = "", szMaxTaken[20] = "";

char szThisRoll[20];
char szNextRoll[20];
char szPrevRoll[20];

char **szFileNames = NULL;

#define MAX_NAME_LEN         12
#define MAX_TITLE_LEN        800 
#define MAX_SHORT_TITLE_LEN  400 
#define MAX_NUM_TITLES       400

typedef struct tagTitles
{
    char szName[MAX_NAME_LEN];
    char szTitle[MAX_TITLE_LEN];
    char szShortTitle[MAX_SHORT_TITLE_LEN];
} Titles;

Titles titles[MAX_NUM_TITLES];
char szDriveTitles1[256] = "";
char szDriveTitles2[256] = "";
char *pRootFolder = NULL;


BOOL CopyAFile(
    LPCSTR lpExistingFileName,
    LPCSTR lpNewFileName,
    BOOL bFailIfExists
)
{
    BOOL bRet = CopyFile(lpExistingFileName, lpNewFileName, bFailIfExists);
    printf("Copying %s to %s [%s]\n", lpExistingFileName, lpNewFileName, bRet ? "success" : "fail");
    return bRet;
}


BOOL GetTakenDate(char *pFileName, char *pDate)
{
    pDate[0] = 0; ;
    EXIFINFO exifinfo;

    memset(&exifinfo, 0, sizeof(EXIFINFO));

    Cexif exif(&exifinfo);

    FILE* hFile = fopen(pFileName, "rb");

    if (hFile)
    {

        exif.DecodeExif(hFile);
        fclose(hFile);

        if (exif.m_exifinfo->IsExif)
        {
            sprintf(pDate, "%02d/%02d/%04d",
                atoi(&exif.m_exifinfo->DateTime[8]),
                atoi(&exif.m_exifinfo->DateTime[5]),
                atoi(&exif.m_exifinfo->DateTime[0]));
        }
    }
    return pDate[0] != 0;

}

void DeleteFileNames()
{
    for (int n = 0; n < nFiles; n++)
    {
        delete[] szFileNames[n];
    }
    delete[] szFileNames;
    szFileNames = NULL;
    nFiles = 0;
}

void FixFileName(char *szFile)
{
    char *pColon;
    char *pFile = szFile, *pStart;


    for (; isspace((unsigned char)*pFile); pFile++)
        ;

    while ((pColon = strchr(pFile, ':')) && pColon - pFile > 1)
    {
        pFile = pColon + 1;
        while (*pFile == '/' || *pFile == '\\')
            pFile++;
    }

    pStart = pFile;

    for (; *pFile; pFile++)
    {
        if (*pFile == '%' && pFile[1] == '2' && pFile[2] == '0')  // "%20"
        {
            *pFile = ' ';
            for (int i = 1; pFile[i + 1]; i++)
                pFile[i] = pFile[i + 2];
        }
        else if (*pFile == '/')
            *pFile = '\\';
    }
    strcpy(szFile, pStart);

}

BYTE *Scale(BYTE *pBuff, unsigned int nWidth, unsigned int nHeight, unsigned int nX, unsigned int nY, BOOL bSmooth)
{
    nWidth *= 3;
    nX *= 3;

    if (pBuff && nWidth%nX == 0 && nHeight%nY == 0 && nWidth / nX == nHeight / nY)
    {
        unsigned int nScale = nWidth / nX;
        BYTE *pNewBuff = new BYTE[(nX + 1)*(nY + 1)];
        if (pNewBuff)
        {
            memset(pNewBuff, 0, (nX + 1)*(nY + 1));
            for (unsigned int y = 0; y < nHeight; y += nScale)
            {
                for (unsigned int x = 0; x < nWidth; x += nScale * 3)
                {
                    if (bSmooth)
                    {
                        int nMeanR = 0, nMeanG = 0, nMeanB = 0, n = 0;
                        for (unsigned int i = x; i < x + nScale * 3; i += 3)
                            for (unsigned int j = y * nWidth; j < (y + nScale)*nWidth; j += nWidth)
                            {
                                nMeanR += pBuff[j + i];
                                nMeanG += pBuff[j + i + 1];
                                nMeanB += pBuff[j + i + 2];
                                n++;
                            }

                        pNewBuff[x / nScale + y / nScale * nX + 0] = nMeanR / n;
                        pNewBuff[x / nScale + y / nScale * nX + 1] = nMeanG / n;
                        pNewBuff[x / nScale + y / nScale * nX + 2] = nMeanB / n;
                    }
                    else
                        memcpy(&pNewBuff[x / nScale + y / nScale * nX], &pBuff[x + y * nWidth], 3);
                }
            }
            delete[] pBuff;
            pBuff = pNewBuff;
        }

    }
    return pBuff;
}


BYTE *Trim(BYTE *pBuff, unsigned int nWidth, unsigned int nHeight, unsigned int nX, unsigned int nY)
{
    BOOL bPortrait = (nWidth < nHeight);

    nWidth *= 3;
    nX *= 3;

    if (pBuff && nWidth >= nX && nHeight >= nY)
    {
        unsigned int xStart = (nWidth - nX) / 3 / 2 * 3;
        unsigned int yStart = bPortrait ? 0 : (nHeight - nY) / 2;
        BYTE *pNewBuff = new BYTE[(nX + 1)*(nY + 1)];
        if (pNewBuff)
        {
            for (unsigned int y = 0; y < nHeight; y++)
            {
                if (y >= yStart && y < yStart + nY)
                {
                    for (unsigned int x = 0; x < nWidth; x++)
                    {
                        if (x >= xStart && x < (xStart + nX))
                            pNewBuff[x - xStart + (y - yStart)*nX] = pBuff[x + y * nWidth];
                    }
                }
            }
            delete[] pBuff;
            pBuff = pNewBuff;
        }
    }
    return pBuff;
}

BYTE *Normalise(const char *szFileName, unsigned int &nX, unsigned int nY, unsigned int *pnScale, BOOL bSmooth, BOOL bNoFlip, BOOL bNoPortrait = FALSE)
{
    JpegFile jFile;
    unsigned int nWidth = 0, nHeight = 0;
    jFile.GetJPGDimensions(szFileName, &nWidth, &nHeight);
    BOOL bPortrait = nWidth < nHeight;

    if (bPortrait && bNoPortrait)
        return NULL;

    if (bPortrait && !bNoFlip)  // Must be landscape
    {
        nX = (int)((float)nY*((float)nY / (float)nX));
        bPortrait = FALSE;
    }

    if (nWidth < nX || nHeight < nY)
    {
        printf("Image %s needs to be at least %d x %d. It is in fact %d x %d\n", szFileName, nX, nY, nWidth, nHeight);
        return NULL;
    }


    UINT nScale = 1;
    while (nX*(nScale + 1) < nWidth && nY*(nScale + 1) < nHeight)
        nScale++;

    unsigned char *pBuff = jFile.JpegFileToRGB(szFileName, &nWidth, &nHeight);

    if (pBuff)
        pBuff = Trim(pBuff, nWidth, nHeight, nX*nScale, nY*nScale);
    nWidth = nX * nScale;
    nHeight = nY * nScale;
    if (pBuff)
        pBuff = Scale(pBuff, nWidth, nHeight, nX, nY, bSmooth);
    *pnScale = nScale;
    return pBuff;

}

char *GetAdjustedName(const char *szFullName, char *szAdjName, const char *szRoot, BOOL bNeg)
{
    int nLen = strlen(szFullName);
    if (nLen > 2 && stricmp(&szFullName[nLen - 2], "!!") == 0)
    {
        sprintf(szAdjName, ".\\Negatives\\%s", szFullName);
        szAdjName[strlen(szAdjName) - 2] = 0;
    }
    else if (bNeg)
    {
        sprintf(szAdjName, ".\\Negatives\\%s", szFullName);
    }
    else
        strcpy(szAdjName, szFullName);
    return szAdjName;
}

void IThumb(const char *szRoot, bool bNegatives)
{
    char szCommand[512];
    char szDir[256];

    WIN32_FIND_DATA data;
    HANDLE hFind;
    hFind = FindFirstFile("Negatives\\*.jpg", &data);
    bDoNegatives = FALSE;

    if (hFind != INVALID_HANDLE_VALUE)
    {
        FindClose(hFind);
        bDoNegatives = bAllowNegatives;
    }
    else
        bDoNegatives = FALSE;

    if (bThumb)
    {
        GetCurrentDirectory(255, szDir);

        if (!bNegatives)
        {
            sprintf(szCommand, "\"\"C:\\Program Files (x86)\\Easy Thumbnails\\EzThumbs.exe\" \"%s\\*.jpg\" /D=\"%s\\..\\Thumbs\\%s\" /W=180 /H=180 /P=th_\"", szDir, szDir, szRoot);
            printf("%s\n%s\n", szCommand, szDir);
            system(szCommand);
        }
        else
        {
            if (bDoNegatives)
            {
                sprintf(szCommand, "\"\"C:\\Program Files (x86)\\Easy Thumbnails\\EzThumbs.exe\" \"%s\\Negatives\\*.jpg\" /D=\"%s\\..\\Thumbs\\%s\" /W=180 /H=180 /P=nth_\"", szDir, szDir, szRoot);
                system(szCommand);

            }
        }
    }
}


void Thumb(char *szInFile, char *szOutFile, unsigned int nNewWidth, unsigned int nNewHeight, unsigned int *pWidth, unsigned int *pHeight, BOOL bThumb, BOOL bSmooth, const char *szRoot, BOOL bNeg)
{
    char szAdjustedName[256];
    GetAdjustedName(szInFile, szAdjustedName, szRoot, bNeg);
    BOOL bDoThumb = FALSE;

    if (bAuto)
    {
        WIN32_FIND_DATA data1;
        HANDLE hFile1 = FindFirstFile(szAdjustedName, &data1);
        if (hFile1 != INVALID_HANDLE_VALUE)
        {
            WIN32_FIND_DATA data2;
            HANDLE hFile2 = FindFirstFile(szOutFile, &data2);
            if (hFile2 != INVALID_HANDLE_VALUE)
            {
                /*                WIN32_FIND_DATA data3 ;
                HANDLE hFile3 = FindFirstFile ( ".", &data3 ) ;
                if ( hFile3 != INVALID_HANDLE_VALUE )
                {
                int c1 = CompareFileTime(&data1.ftLastWriteTime, &data2.ftLastWriteTime ) ;
                int c2 = CompareFileTime(&data1.ftLastWriteTime, &data3.ftLastAccessTime ) ;

                  if ( c1 >0 && c2 < 0)
                  bDoThumb = TRUE ;
                  FindClose (hFile3) ;
                }*/
                FindClose(hFile2);
            }
            else
                bDoThumb = TRUE;

            FindClose(hFile1);
        }
    }

    if (bThumb || bDoThumb)
    {
        unsigned int nScale = 1; ;
        printf("Creating Thumbprint of %s\n", szInFile);
        unsigned char *p1 = Normalise(szAdjustedName, nNewWidth, nNewHeight, &nScale, bSmooth, FALSE);
        if (p1)
        {
            JpegFile::RGBToJpegFile(szOutFile, p1, nNewWidth, nNewHeight, TRUE, nQuality);
            *pWidth = nNewWidth;
            *pHeight = nNewHeight;
        }
    }
    else
        JpegFile::GetJPGDimensions(szOutFile, pWidth, pHeight);


}

int GetFileTitle(char *pFileName, char *szName = NULL)
{
    int n = -1;
    char *p = strchr(pFileName, '.');
    char *p2 = strrchr(pFileName, '.');
    if (p == NULL)
        p = pFileName + strlen(pFileName) - 1;
    if (p2 == NULL)
        p2 = pFileName + strlen(pFileName);

    if (szName)
        szName[0] = 0;

    while (p >= pFileName && (*p<'0' || *p>'9')) // Find any numbers in filename
        p--;

    if (p >= pFileName)
    {
        while (p > pFileName && *p >= '0' && *p <= '9')
            p--;
        if (*p <'0' || *p > '9')
            p++;

        int nLen = p2 - p;
        n = atoi(p);
        if (szName)
        {
            if (n == 0)
            {
                strncpy(szName, p, nLen);
                szName[nLen] = 0;
            }
            else
                sprintf(szName, "%d", n);
        }
    }
    else
    {
        if (szName)              // No number found
        {

            if (p2)
            {
                strncpy(szName, pFileName, p2 - pFileName);
                szName[p2 - pFileName] = 0;
            }
            else
                strcpy(szName, pFileName);
        }

    }

    return n;
}

int CheckForDate(char *pName, char*pRet = NULL)
{
    /*
    char szName [MAX_TITLE_LEN] ;

      char *p= NULL ;
      if ( pName )
      {
      strcpy ( szName, pName ) ;
      p = strchr ( szName, '.' ) ;

        if ( p != NULL)
        *p = 0;
        }

          if ( pName && strlen (szName) == 4 )
          {
          int nDay    = (szName[0]-'0')*10 + (szName[1]-'0') ;
          int nMonth  = (szName[2]-'0')*10 + (szName[3]-'0') ;

            if ( nDay > 0 && nDay <= 31 && nMonth > 0 && nMonth <= 12 )
            {
            if ( pRet )
            sprintf ( pRet, "%02d/%02d", nDay, nMonth ) ;
            return nMonth*32+nDay ;
            }
    }        */
    return 0;
}

int compare(const void *arg1, const void *arg2)
{

    char *p1 = *(char**)arg1;
    char *p2 = *(char**)arg2;

    char szTitle1[256], szTitle2[256];

    int n1 = GetFileTitle(p1, szTitle1);
    int n2 = GetFileTitle(p2, szTitle2);

    int d1 = CheckForDate(szTitle1);
    int d2 = CheckForDate(szTitle2);

    if (bSortByTime)
    {
        int nRet = 0;
        FILE* hFile1 = fopen(p1, "rb");

        if (hFile1)
        {
            FILE* hFile2 = fopen(p2, "rb");
            if (hFile2)
            {
                EXIFINFO exifinfo1, exifinfo2;

                memset(&exifinfo1, 0, sizeof(EXIFINFO));
                memset(&exifinfo2, 0, sizeof(EXIFINFO));

                Cexif exif1(&exifinfo1);
                exif1.DecodeExif(hFile1);
                Cexif exif2(&exifinfo2);
                exif2.DecodeExif(hFile2);
                fclose(hFile2);

                if (exif1.m_exifinfo->IsExif && exif2.m_exifinfo->IsExif)
                {
                    nRet = strcmp(exif1.m_exifinfo->DateTime, exif2.m_exifinfo->DateTime);
                }
                else
                {
                    WIN32_FIND_DATA data1;
                    HANDLE hFile1 = FindFirstFile(p1, &data1);
                    if (hFile1 != INVALID_HANDLE_VALUE)
                    {
                        WIN32_FIND_DATA data2;
                        HANDLE hFile2 = FindFirstFile(p2, &data2);
                        if (hFile2 != INVALID_HANDLE_VALUE)
                        {
                            nRet = CompareFileTime(&data1.ftCreationTime, &data2.ftCreationTime);
                            FindClose(hFile2);
                        }
                        FindClose(hFile1);
                    }

                }
            }

            fclose(hFile1);
        }

        return nRet;
    }
    int f1 = -1, f2 = -1;
    for (int n = 0; n < nTitles; n++)
    {
        if (stricmp(szTitle1, titles[n].szName) == 0)
            f1 = n;
        if (stricmp(szTitle2, titles[n].szName) == 0)
            f2 = n;

        if (f1 != -1 && f2 != -1)
            break;
    }

    if (f1 != -1 && f2 != -1 && bDoSortByTitle)
        return f1 - f2;

    // if ( d1 > 0 && d2 > 0 )
    //    return d1 - d2 ;

    if (n1 >= 0 && n2 >= 0 && n1 != n2)
        return n1 - n2;

    return (stricmp(p1, p2));

}

char *GetTextTitle(char *szFile)
{
    char *pRet = szFile;
    BOOL bFound = FALSE;

    for (int i = 0; i < nTitles; i++)
    {
        if (stricmp(titles[i].szName, szFile) == 0)
        {
            bFound = TRUE;
            if (titles[i].szTitle[0] != 0)
            {
                pRet = titles[i].szTitle;
                break;
            }
            else
            {
                pRet = titles[i].szShortTitle;
                break;
            }
        }
    }

    return pRet;

}

char *GetTitle(char *szFile)
{
    char *pRet = szFile;
    static char szDateRet[6];
    static char szTitle[1024];
    BOOL bFound = FALSE;

    for (int i = 0; i < nTitles; i++)
    {
        if (stricmp(titles[i].szName, szFile) == 0)
        {
            bFound = TRUE;
            if (titles[i].szTitle[0] != 0)
            {
                pRet = titles[i].szTitle;
                break;
            }
            else
            {
                pRet = titles[i].szShortTitle;
                break;
            }
        }
    }
    if (!bFound)
    {
        for (int i = 0; i < nTitles; i++)
        {
            if (atoi(titles[i].szName) == atoi(szFile))
            {
                bFound = TRUE;
                if (titles[i].szTitle[0] != 0)
                {
                    pRet = titles[i].szTitle;
                    break;
                }
                else
                {
                    pRet = titles[i].szShortTitle;
                    break;
                }
            }
        }
    }

    if (CheckForDate(pRet, szDateRet))
        return szDateRet;
    if (stricmp(szFile, pRet) == 0)
        return pRet;

    sprintf(szTitle, "%s %s", szFile, pRet);
    return szTitle;
}

char *GetShortTitle(char *szFile)
{
    static char szDateRet[6];
    char *pRet = szFile;
    static char szTitle[1024];

    BOOL bFound = FALSE;
    for (int i = 0; i < nTitles; i++)
    {
        if (stricmp(titles[i].szName, szFile) == 0)
        {
            bFound = TRUE;
            if (titles[i].szShortTitle[0] != 0)
            {
                pRet = titles[i].szShortTitle;
                break;
            }
            else
            {
                pRet = titles[i].szTitle;
                break;
            }
        }
    }

    if (!bFound)
    {
        for (int i = 0; i < nTitles; i++)
        {
            if (atoi(titles[i].szName) == atoi(szFile))
            {
                bFound = TRUE;
                if (titles[i].szShortTitle[0] != 0)
                {
                    pRet = titles[i].szShortTitle;
                    break;
                }
                else
                {
                    pRet = titles[i].szTitle;
                    break;
                }
            }
        }
    }

    if (CheckForDate(pRet, szDateRet))
        return szDateRet;

    if (stricmp(szFile, pRet) == 0)
        return pRet;

    sprintf(szTitle, "%s %s", szFile, pRet);
    return szTitle;
}

void CreateSubPage(char *szFullName, char *szName, const char *szRoot, const char *szNxt, const char *szPrv, int n, char *szPath, BOOL bHighlight, BOOL bNeg)
{
    char szFileName[256], szNext[256], szPrev[256], szLongName[256];
    char szNeg[2] = "";
    char szDate[16] = "";

    if (bDoDate)
    {
        GetTakenDate(szFullName, szDate);
    }

    if (bNeg)
        strcpy(szNeg, "n");

    sprintf(szFileName, "htm\\%s%s.htm", szNeg, szName);
    _splitpath(szNxt, 0, 0, szNext, 0);
    _splitpath(szPrv, 0, 0, szPrev, 0);

    int nFile = GetFileTitle(szFullName, szLongName);
    char szAdjustedName[256];
    GetAdjustedName(szFullName, szAdjustedName, szRoot, bNeg);

    FILE *pFile = fopen(szFileName, "w");
    if (pFile == NULL)
    {
        printf("Unable to create file %s", szFileName);
        return;
    }

    fprintf(pFile,
        "<html>\n"
        "   <head>\n"
        "       <title>%s</title>\n"
        "       <LINK href=\"../../main.css\" type=text/css rel=stylesheet>\n"
        "   </head>\n"
        "   <body>\n"
        "       <p>\n"
        "           %s (%s) %s %s\n"
        "           <a href=\"%s%s.htm\">Previous</a> \n"
        "           <a href=\"%s%s.htm\">Next</a> \n"
        "           <a href=\"../%s.htm\">%s</a> \n"
        ,
        szGlobalShortTitle, szGlobalShortTitle, szName, szDate,
        bMinutes ? " " : 
        "       </p>\n"
        "       <p>\n",
        szNeg, szNext, szNeg, szPrev,
        szRoot, !bHighlight ? szThisRoll : "Home");

    if (!bHighlight)
    {
        if (pPrev && pPrev[0] != 0)
        {
            if (strcmp(pPrev, "x") != 0)
                fprintf(pFile, 
        "           <a href=\"../%s\">%s</a> \n", pPrev, szPrevRoll);
        }
        else if (!bAuto)
            fprintf(pFile, 
        "           <a href=\"../../%d/%d.htm\">%s</a> \n", atoi(szRoot) - 1, atoi(szRoot) - 1, szPrevRoll);

        if (pNext && pNext[0] != 0)
        {
            if (strcmp(pNext, "x") != 0)
                fprintf(pFile, 
        "           <a href=\"../%s\">%s</a> ", pNext, szNextRoll);
        }
        else if (!bAuto)
            fprintf(pFile, 
        "           <a href=\"../../%d/%d.htm\">%s</a> \n", atoi(szRoot) + 1, atoi(szRoot) + 1, szNextRoll);
    }

    unsigned int nWidth, nHeight;
    JpegFile jFile;
    jFile.GetJPGDimensions(szAdjustedName, &nWidth, &nHeight);
    if (nHeight > nImgHeight)
        nHeight = nImgHeight;

    if (!bNeg)
        fprintf(pFile, 
            "       </p>\n"
            "       <p>\n"
            "           <table border = \"%d\">\n"
            "               <caption align=\"bottom\">%s</Caption>\n"
            "               <tr>\n"
            "                   <td>\n"
            "                       <a href=\"../%s%s\"><img src=\"../%s%s\" height=\"%d\"></a>\n"
            "                   </td>\n"
            "               </tr>\n"
            "           </table>\n"
            "       </p>\n"
            
            , bMinutes ? 1 : 10, GetTitle(szLongName), szPath, szAdjustedName, szPath, szAdjustedName, nHeight);
    else
        fprintf(pFile,

            "       <p>\n"
            "           <table border = \"%d\">\n"
            "               <caption align=\"bottom\">%s</Caption>\n"
            "               <tr>\n"
            "                   <td>\n"
            "                       <a href=\".%s\"><img src=\".%s\" height=\"%d\"></a>\n"
            "                   </td>\n"
            "               </tr>\n"
            "           </table>\n"
            "       </p>\n"
            

            , bMinutes ? 1 : 10, GetTitle(szLongName), szAdjustedName, szAdjustedName, nHeight);

    fprintf(pFile, 
            "   </body>\n"
            "</html>");

    fclose(pFile);

}

#define MAXTITLES 3113

void DeleteTitles(char ***pTitles)
{
    if (pTitles && *pTitles)
    {
        for (int i = 0; i < MAXTITLES; i++)
        {
            if ((*pTitles)[i] != NULL)
                delete[](*pTitles)[i];
        }
        delete[] * pTitles;
        *pTitles = NULL;
    }
}

void ConvertToJPG(char *szFileName, int nWidth, int nHeight)
{
    char szOutFile[_MAX_PATH];
    strcpy(szOutFile, szFileName);
    strcat(szOutFile, ".jpg");
    int nSize = nWidth * nHeight * 3;


    FILE *pIn = fopen(szFileName, "rb");
    if (pIn)
    {
        fseek(pIn, 0, SEEK_END);
        if (ftell(pIn) < nSize)
        {
            printf("File needs to be at least %d bytes in size\n", nSize);
        }
        else
        {
            char *pBuffer = new char[nSize];
            if (pBuffer)
            {
                fseek(pIn, 0, SEEK_SET);
                fread(pBuffer, nSize, 1, pIn);
                JpegFile::RGBToJpegFile(szOutFile, (unsigned char *)pBuffer, nWidth, nHeight, TRUE, 100);
                printf("Created output file %s\n", szOutFile);
            }
        }
        fclose(pIn);
    }

}

void ParseCommandLine(char *szLine, int i)
{
    char szParam[256];
    char *p = szLine;

    while (*p)
    {
        char *l = szParam;
        while (*p && !isspace((unsigned char)*p))
            *l++ = *p++;
        *l = 0;
        while (*p && isspace((unsigned char)*p))
            p++;
        if (szParam[0] == '-')
        {
            char *pParam = strdup(szParam);
            switch (pParam[1])
            {
            case 'k':
                bTaken = TRUE;
                break;
            case 'd':
                strcpy(szGlobalShortTitle, &pParam[2]);
                break;
            case 'u':
                szDuplicate = &pParam[2];
                bUnique = TRUE;
                break;
            case 'c':
                nCCols = nCols = atoi(&pParam[2]);
                break;
            case 'r':
                if (stricmp(&pParam[1], "rs") == 0)
                {
                    bRenameSort = TRUE;
                    if (__argc == 4)
                        rsName = __argv[3];
                }
                else
                {
                    nCRows = atoi(&pParam[2]);
                    bReverse = TRUE;
                }
                break;
            case 'n':
                pNext = &pParam[2];
                break;
            case 'p':
                pPrev = &pParam[2];
                break;
            case 't':
                if (pParam[2] == 'h')
                    nThumbHeight = atoi(&pParam[3]);
                else if (pParam[2] == 'w')
                    nThumbWidth = atoi(&pParam[3]);
                else
                {
                    szTitlesFile = &pParam[2];
                    nTop = atoi(&pParam[2]);
                }
                break;
            case 's':
                szShortFile = &pParam[2];
                nSmall = atoi(&pParam[2]);
                break;
            case '4':
                szCrunchFile = &pParam[2];
                szFull = &pParam[2];
                break;
            case 'm':
                if (strcmp(&pParam[1], "minutes") == 0)
                    bMinutes = TRUE;
                else
                    szMissing = &pParam[2];
                break;
            case 'b':
                szBlank = &pParam[2];
                nBig = atoi(&pParam[2]);
                break;
            case 'z':
                bNoMissing = FALSE;
                bCopy = TRUE;
                break;
            case 'h':
                if (stricmp(&pParam[1], "height") == 0)
                    nImgHeight = atoi(__argv[++i]);
                else
                    bThumb = TRUE;
                break;
            case 'q':
                bSmooth = FALSE;
                break;
            case 'x':
                bCrunch = TRUE;
                break;
            case 'l':
                bPixellate = TRUE;
                szPixelFile = &pParam[2];
                break;
            case 'L':
                bLes = TRUE;
                break;
            case 'y':
                bScanTooSmall = TRUE;
                break;
            case 'v':
                bAPAY = TRUE;
                break;
            case 'w':
                bSlideshow = TRUE;
                break;
            case 'i':
                bDoIndex = TRUE;
                break;
            case '1':
                bStartIndex = TRUE;
                break;
            case '2':
                bEndIndex = TRUE;
                break;
            case 'o':
                bDoSortByTitle = TRUE;
                break;
            case 'e':
                bDoMore = TRUE;
                break;
            case '3':
                bRenameSort = TRUE;
                break;
            case 'f':
                bDoFavourites = TRUE;
                break;

            case 'g':
                if (__argc > i + 2)
                    ConvertToJPG(__argv[1], atoi(__argv[i + 1]), atoi(__argv[i + 2]));
                else
                    printf("Convert to jpg need width and height\n");
                return;
            case 'j':
                bDoDate = TRUE;
                break;
            case '5':
                nQuality = atoi(&pParam[2]);
                if (nQuality < 50)
                    nQuality = 50;
                if (nQuality > 100)
                    nQuality = 100;
                break;
            case '6':
                bDoSkip = FALSE;
                break;

            }
        }

    }
}

BOOL MkRecursiveDir(char *pNewDir, bool bHasFile = false)
{
    char szCurr[256];
    char szNew[256] = { 0 };
    BOOL bRet = TRUE;
    char *pDir = NULL;

    GetCurrentDirectory(255, szCurr);

    strcpy(szNew, pNewDir);
    while (!SetCurrentDirectory(szNew) && (pDir = strrchr(szNew, '\\')) != NULL)
    {
        *pDir = 0;
    }
    while (pDir && *(pDir + 1) && (!bHasFile || *(pDir + strlen(pDir + 1) + 2)) &&
        (bRet = CreateDirectory(pDir + 1, NULL)))
    {
        SetCurrentDirectory(pDir + 1);
        pDir = pDir + strlen(pDir + 1) + 1;

    }

    SetCurrentDirectory(szCurr);
    return bRet;
}

BOOL MkRecursiveFileDir(char *pFileDir)
{
    char szCurr[256];
    char szNew[256];
    BOOL bRet = FALSE;
    char *pDir;

    GetCurrentDirectory(255, szCurr);

    strcpy(szNew, pFileDir);
    pDir = strrchr(szNew, '\\');
    if (pDir)
    {
        *pDir = 0;
        bRet = MkRecursiveDir(szNew);
    }

    SetCurrentDirectory(szCurr);
    return bRet;
}

void CopyTitlesToGoogleDrive(char *szFolder, char *szRoot, char *szFileName, char **ppFileName, char *szFullName1, char *szFullName2, char *szFullName3)
{
    sprintf(szFullName1, "%s\\%s\\%s\\%s", szDriveTitles1, pRootFolder, szRoot, szFileName);
    sprintf(szFullName2, "%s\\%s\\%s\\%s", szDriveTitles2, pRootFolder, szRoot, szFileName);
    sprintf(szFullName3, "%s\\%s", szFolder, szFileName);

    WIN32_FIND_DATA data1, data2, data3;
    HANDLE hFile1, hFile2, hFile3;

    hFile1 = FindFirstFile(szFullName1, &data1);
    hFile2 = FindFirstFile(szFullName2, &data2);
    hFile3 = FindFirstFile(szFullName3, &data3);

    if (hFile1 != INVALID_HANDLE_VALUE && hFile3 != INVALID_HANDLE_VALUE)
    {
        int nComp = CompareFileTime(&data1.ftLastWriteTime, &data3.ftLastWriteTime);
        if (nComp > 0)
        {
            MkRecursiveDir(szFullName3, true);
            CopyAFile(szFullName1, szFullName3, false);
        }
        if (nComp < 0)
        {
            MkRecursiveDir(szFullName1, true);
            CopyAFile(szFullName3, szFullName1, false);
        }
        *ppFileName = szFullName3;
    }
    else if (hFile2 != INVALID_HANDLE_VALUE && hFile3 != INVALID_HANDLE_VALUE)
    {
        int nComp = CompareFileTime(&data2.ftLastWriteTime, &data3.ftLastWriteTime);
        if (nComp > 0)
        {
            MkRecursiveDir(szFullName3, true);
            CopyAFile(szFullName2, szFullName3, false);
        }
        if (nComp < 0)
        {
            MkRecursiveDir(szFullName2, true);
            CopyAFile(szFullName3, szFullName2, false);
        }
        *ppFileName = szFullName3;
    }
    else if (hFile1 != INVALID_HANDLE_VALUE && hFile3 == INVALID_HANDLE_VALUE)
    {
        MkRecursiveDir(szFullName3, true);
        CopyAFile(szFullName1, szFullName3, false);
        *ppFileName = szFullName1;
    }
    else if (hFile2 != INVALID_HANDLE_VALUE && hFile3 == INVALID_HANDLE_VALUE)
    {
        MkRecursiveDir(szFullName3, true);
        CopyAFile(szFullName2, szFullName3, false);
        *ppFileName = szFullName2;
    }
    else if (hFile1 == INVALID_HANDLE_VALUE && hFile3 != INVALID_HANDLE_VALUE)
    {
        MkRecursiveDir(szFullName2, true);
        CopyAFile(szFullName3, szFullName2, false);
        *ppFileName = szFullName3;
    }
    else if (hFile2 == INVALID_HANDLE_VALUE && hFile3 != INVALID_HANDLE_VALUE)
    {
        MkRecursiveDir(szFullName2, true);
        CopyAFile(szFullName3, szFullName2, false);
        *ppFileName = szFullName3;
    }
    if (hFile1 != INVALID_HANDLE_VALUE)
        FindClose(hFile1);
    if (hFile2 != INVALID_HANDLE_VALUE)
        FindClose(hFile2);
    if (hFile3 != INVALID_HANDLE_VALUE)
        FindClose(hFile3);
}

void ReadTitles(char *szFolder, char *szRoot, char *szFileName)
{
    char *pFileName = NULL;
    char szFullName1[MAX_TITLE_LEN] = "";
    char szFullName2[MAX_TITLE_LEN] = "";
    char szFullName3[MAX_TITLE_LEN] = "";


    memset(titles, 0, MAX_NUM_TITLES * sizeof(Titles));
    char szLine[MAX_TITLE_LEN];

    if (szFileName)
    {
        FILE *f = NULL;

        CopyTitlesToGoogleDrive(szFolder, szRoot, szFileName, &pFileName, szFullName1, szFullName2, szFullName3);

        if (pFileName)
        {
            f = fopen(pFileName, "r");
            printf("Attempting to open %s %s\n", pFileName, f ? "success" : "fail");
        }

        if (f == NULL && bAuto)
        {
            if (szFullName3[0] != 0 && MkRecursiveFileDir(szFullName3))
            {
                f = fopen(szFullName3, "w");
                printf("Attempting to open %s %s\n", szFullName3, f ? "success" : "fail");
            }

            if (f)
            {
                char *pName = strrchr(szFolder, '\\');
                if (!pName)
                    pName = szFolder;
                else
                    pName++;
                if (!bLes)
                    fprintf(f, "Title: %s\n", pName);
                else
                    fprintf(f, "Map: %s\n", pName);

                if (bDoDate)
                    fprintf(f, "-j\n");

                for (int i = 0; i < nFiles; i++)
                {
                    fprintf(f, "%d\n", GetFileTitle(szFileNames[i]));
                }

                fclose(f);
            }
            f = NULL;
            if (szFullName2[0] != 0)
            {
                f = fopen(szFullName2, "r");
                printf("Attempting to open %s %s\n", szFullName2, f ? "success" : "fail");
            }
            if (f == NULL)
            {
                f = fopen(szFullName1, "r");
                printf("Attempting to open %s %s\n", szFullName1, f ? "success" : "fail");
            }
        }
        if (f)
        {
            nTitles = 0;
            while (fgets(szLine, MAX_TITLE_LEN - 1, f))
            {
                int nStartName, nEndName;
                int nStartFull, nEndFull;
                int nStartShort, nEndShort;
                int nLen = strlen(szLine);

                if (szLine[0] == '-')
                {
                    ParseCommandLine(szLine, 0);
                    continue;
                }
                for (nStartName = 0; nStartName < nLen && isspace((unsigned char)szLine[nStartName]); nStartName++)
                    ;
                for (; nLen > 0 && isspace((unsigned char)szLine[nLen - 1]); nLen--)
                    szLine[nLen - 1] = 0;

                if ((szLine[nStartName]<'0' || szLine[nStartName]>'9') && szLine[nStartName] != 0)
                {
                    strcpy(szGlobalTitle, &szLine[nStartName]);
                    if (szGlobalShortTitle[0] == 0)
                    {
                        strcpy(szGlobalShortTitle, szGlobalTitle);
                        int nLen = strlen(szGlobalShortTitle);
                        if (nLen > 0 && szGlobalShortTitle[nLen - 1] == '\\')
                            szGlobalShortTitle[--nLen] = 0;
                        if (nLen > 0 && szGlobalShortTitle[nLen - 1] != '.')
                            strcat(szGlobalShortTitle, ".");

                    }


                    while (nLen > 0 && szLine[nLen - 1] == '\\')
                    {
                        if (fgets(szLine, MAX_TITLE_LEN - 1, f) == 0)
                            break;

                        nLen = strlen(szLine);
                        for (; nLen > 0 && isspace((unsigned char)szLine[nLen - 1]); nLen--)
                            szLine[nLen - 1] = 0;
                        strcpy(&szGlobalTitle[strlen(szGlobalTitle) - 1], "<br>");
                        strcat(szGlobalTitle, szLine);
                    }

                    continue;
                }
                if (szLine[nStartName] == '#')
                    continue;

                for (nEndName = nStartName; nEndName < nLen && !isspace((unsigned char)szLine[nEndName]); nEndName++)
                    ;

                for (nStartFull = nEndName + 1; nStartFull < nLen && isspace((unsigned char)szLine[nStartFull]); nStartFull++)
                    ;

                for (nEndFull = nStartFull; nEndFull < nLen && szLine[nEndFull] != '|'; nEndFull++)
                    ;

                for (nStartShort = nEndFull + 1; nStartShort < nLen && isspace((unsigned char)szLine[nStartShort]); nStartShort++)
                    ;

                for (nEndShort = nStartShort; nEndShort < nLen; nEndShort++)
                    ;

                for (; nEndFull > nStartFull && (isspace((unsigned char)szLine[nEndFull - 1])); nEndFull--)
                    ;

                for (; nEndShort > nStartShort && isspace((unsigned char)szLine[nEndShort - 1]); nEndShort--)
                    ;

                strncpy(titles[nTitles].szName, &szLine[nStartName], nEndName - nStartName);
                strncpy(titles[nTitles].szTitle, &szLine[nStartFull], nEndFull - nStartFull);
                strncpy(titles[nTitles].szShortTitle, &szLine[nStartShort], nEndShort - nStartShort);

                nTitles++;
            }
            fclose(f);
        }
        CopyTitlesToGoogleDrive(szFolder, szRoot, szFileName, &pFileName, szFullName1, szFullName2, szFullName3);
    }
}


BOOL IsKnown(int n, char *szStr)
{
    if (szStr == NULL)
        return (!IsKnown(n, szMissing) && !IsKnown(n, szBlank) && !IsKnown(n, szDuplicate));

    char szNum[4];
    sprintf(szNum, "%d", n);
    char *szFound = strstr(szStr, szNum);
    BOOL bFound = FALSE;
    for (; szFound && (szFound = strstr(szFound, szNum)) != NULL; szFound++)
    {
        if (szFound > szStr && szFound[-1] != ',')
            continue;
        if (szFound[strlen(szNum)] != 0 && szFound[strlen(szNum)] != ',')
            continue;
        bFound = TRUE;
        break;
    }
    return bFound;
}



int FindMissing(FILE *pFile, char *szStr)
{
    int nLast = 0;
    int nMissing = 0;
    for (int i = 0; i < nFiles; i++)
    {
        int n = GetFileTitle(szFileNames[i]);
        if (n - nLast > 1)
        {
            for (int j = nLast + 1; j < n; j++)
            {
                if (IsKnown(j, szStr))
                {
                    fprintf(pFile, "%d ", j);
                    nMissing++;
                }
            }
        }
        nLast = n;
    }


    if (nLast <= 13)
        for (int j = nLast + 1; j <= 12; j++)
        {
            if (IsKnown(j, szStr))
            {
                fprintf(pFile, "%d ", j);
                nMissing++;
            }
        }
    else if (nLast <= 25)
        for (int j = nLast + 1; j <= 24; j++)
        {
            if (IsKnown(j, szStr))
            {
                fprintf(pFile, "%d ", j);
                nMissing++;
            }
        }
    else if (nLast <= 37)
        for (int j = nLast + 1; j <= 36; j++)
        {
            if (IsKnown(j, szStr))
            {
                fprintf(pFile, "%d ", j);
                nMissing++;
            }
        }

    return nMissing;

}

char * NegativeDir(const char *szFolder, char *szNeg)
{
    if (!bDoNegatives)
        return NULL;
    sprintf(szNeg, "%s\\Negatives", szFolder);
    return szNeg;
}

int CountFiles(const char *szFile, const char *szFolder, BOOL bRecurse)
{
    int nFiles = 0;
    WIN32_FIND_DATA data;
    HANDLE hFile = FindFirstFile(szFile, &data);
    if (hFile != INVALID_HANDLE_VALUE)
    {
        do
        {
            if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) == 0 && data.nFileSizeHigh == 0 && data.nFileSizeLow > MIN_SIZE && strstr(data.cFileName, "_original") == NULL)
                nFiles++;
        } while (FindNextFile(hFile, &data));
        FindClose(hFile);
    }

    if (szFolder && !bRecurse)
    {
        char szCurr[256], szNeg[256];
        GetCurrentDirectory(255, szCurr);
        if (NegativeDir(szFolder, szNeg) && SetCurrentDirectory(szNeg))
        {
            nFiles += CountFiles(szFile, NULL, FALSE);
            SetCurrentDirectory(szCurr);
        }
    }

    if (bRecurse)
    {
        hFile = FindFirstFile("*.*", &data);
        if (hFile != INVALID_HANDLE_VALUE)
        {
            do
            {
                if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) != 0
                    && stricmp(data.cFileName, ".") != 0 && stricmp(data.cFileName, "..") != 0
                    && data.cFileName[0] != '~')

                {
                    if (SetCurrentDirectory(data.cFileName))
                    {
                        nFiles += CountFiles(szFile, szFolder, TRUE);
                        SetCurrentDirectory("..");
                    }
                }

            } while (FindNextFile(hFile, &data));
            FindClose(hFile);
        }
    }
    return nFiles;

}

int CompareDate(char *date1, char *date2)
{
    int d1 = atoi(date1);
    int d2 = atoi(date2);
    int m1 = atoi(&date1[3]);
    int m2 = atoi(&date2[3]);
    int y1 = atoi(&date1[6]);
    int y2 = atoi(&date2[6]);

    if (y1 != y2)
        return y1 - y2;
    if (m1 != m2)
        return m1 - m2;
    return d1 - d2;
}

int ReadFiles(const char *szFile, const char *szFolder, BOOL bRecurse, char *szDir, int nStart = 0, bool bNeg = FALSE)
{
    WIN32_FIND_DATA data;

    int nFile = nStart;
    HANDLE hFile = FindFirstFile(szFile, &data);
    if (hFile != INVALID_HANDLE_VALUE)
    {
        do
        {
            if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) == 0 && data.nFileSizeHigh == 0 && data.nFileSizeLow > MIN_SIZE && strstr(data.cFileName, "_original") == NULL)
            {
                char szPath[256];
                if (szDir[0] != 0)
                    sprintf(szPath, "%s/%s", szDir, data.cFileName);
                else
                {
                    if (!bNeg)
                        sprintf(szPath, "%s", data.cFileName);
                    else
                        sprintf(szPath, "%s!!", data.cFileName);
                }
                szFileNames[nFile] = new char[strlen(szPath) + 1];
                strcpy(szFileNames[nFile], szPath);
                if (bTaken)
                {
                    char szTaken[20];
                    GetTakenDate(szFileNames[nFile], szTaken);
                    if (szTaken[0] != 0 && atoi(szTaken) > 0)
                    {
                        if (szMaxTaken[0] == 0 || CompareDate(szTaken, szMaxTaken) > 0)
                            strcpy(szMaxTaken, szTaken);
                        if (szMinTaken[0] == 0 || CompareDate(szTaken, szMinTaken) < 0)
                            strcpy(szMinTaken, szTaken);
                    }
                }
                nFile++;
            }
        } while (FindNextFile(hFile, &data) && nFile <= nFiles);
        FindClose(hFile);
    }

    if (szFolder && !bRecurse)
    {
        char szCurr[256], szNeg[256];
        GetCurrentDirectory(255, szCurr);
        if (NegativeDir(szFolder, szNeg) && SetCurrentDirectory(szNeg))
        {
            nFile = ReadFiles(szFile, NULL, FALSE, szDir, nFile, TRUE);
            SetCurrentDirectory(szCurr);
        }
    }

    if (bRecurse)
    {
        hFile = FindFirstFile("*.*", &data);
        if (hFile != INVALID_HANDLE_VALUE)
        {
            do
            {
                if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) != 0
                    && stricmp(data.cFileName, ".") != 0 && stricmp(data.cFileName, "..") != 0
                    && data.cFileName[0] != '~')
                {
                    if (SetCurrentDirectory(data.cFileName))
                    {
                        char szPath[256];
                        if (szDir[0] != 0)
                            sprintf(szPath, "%s/%s", szDir, data.cFileName);
                        else
                            sprintf(szPath, "%s", data.cFileName);

                        nFile = ReadFiles(szFile, szFolder, TRUE, szPath, nFile);
                        SetCurrentDirectory("..");
                    }
                }
            } while (FindNextFile(hFile, &data) && nFile <= nFiles);
            FindClose(hFile);
        }
    }
    return nFile;
}


int ScanFiles(const char *szFile, const char *szFolder, BOOL bRecurse)
{
    nFiles = CountFiles(szFile, szFolder, bRecurse);
    if (nFiles > 0)
    {
        szFileNames = new char*[nFiles];
        ReadFiles(szFile, szFolder, bRecurse, "");
    }
    return nFiles;
}

void DoIndex(const char *szRoot, char *szPath)
{
    char *pDir = strrchr(szPath, '\\');
    while (pDir && *--pDir != '\\')
        ;
    pDir++;


    FILE* pFile = fopen("..\\..\\ ", "a");
    if (pFile)
    {
        fprintf(pFile, "<a href = \"%s\\%s.htm\" name = \"%s\">%s. %s</a><br>\n", pDir, szRoot, szRoot, szRoot, szGlobalShortTitle);
        fclose(pFile);
    }


}

int CompareName(const char *arg1, const char *arg2)
{
    BOOL bIsAllDigits = TRUE;
    unsigned int i;
    for (i = 0; i < strlen(arg1); i++)
        if (!isdigit(arg1[i]))
            bIsAllDigits = FALSE;
    for (i = 0; i < strlen(arg2); i++)
        if (!isdigit(arg2[i]))
            bIsAllDigits = FALSE;

    if (bIsAllDigits || atoi(arg1) != atoi(arg2))
        return (atoi(arg1) - atoi(arg2));
    else if (arg1[0] == arg2[0] && atoi(&arg1[1]) != atoi(&arg2[1]))
        return (atoi(&arg1[1]) - atoi(&arg2[1]));
    else
        return strcmp(arg1, arg2);
}


void DoIndexAuto(const char *szRoot, char *szPath)
{
    char szLine[255], szLastName[255] = "";
    char *pDir = strrchr(szPath, '\\');

    char szCurr[256];
    GetCurrentDirectory(255, szCurr);


    while (pDir && *--pDir != '\\')
        ;
    pDir++;

    BOOL bInside = FALSE, bFound = FALSE;

    char szDateStr[256] = "";
    if (bDoDate && szMinTaken[0] != 0 && szMaxTaken[0] != 0 && atoi(szMinTaken) != 0 && atoi(szMaxTaken) != 0)
    {
        if (CompareDate(szMinTaken, szMaxTaken) == 0)
            sprintf(szDateStr, "<font size=\"1\" face=\"Comic Sans MS\"> (%s)</font>", szMinTaken);
        else
            sprintf(szDateStr, "<font size=\"1\" face=\"Comic Sans MS\"> (%s to %s)</font>", szMinTaken, szMaxTaken);
    }

    FILE* pIn = fopen("..\\..\\index.htm", "r");

    if (pIn)
    {
        FILE* pOut = fopen("..\\..\\indext.htm", "w");
        if (pOut)
        {
            while (fgets(szLine, 255, pIn))
            {
                if (strncmp(szLine, "<!--DATE-->", 10) == 0)
                {
                    SYSTEMTIME now;
                    GetLocalTime(&now);

                    fprintf(pOut, "<!--DATE-->Last Updated %02d/%02d/%04d %02d:%02d:%02d\n", now.wDay, now.wMonth, now.wYear, now.wHour, now.wMinute, now.wSecond);
                }
                else if (!bInside)
                {
                    fprintf(pOut, "%s", szLine);
                }
                if (strncmp(szLine, "<!--Start-->", 12) == 0)
                    bInside = TRUE;
                else if (strncmp(szLine, "<!--END-->", 10) == 0)
                {
                    if (!bFound)
                        fprintf(pOut, "<a href = \"%s\\%s.htm\" name = \"%s\">%s. %s</a>%s<br>\n", pDir, szRoot, szRoot, szRoot, szGlobalShortTitle, szDateStr);
                    bFound = TRUE;
                    fprintf(pOut, "%s", szLine);
                    bInside = FALSE;

                }
                else if (bInside)
                {
                    char *p = strchr(szLine, '>');
                    if (p)
                    {
                        char *p2 = strchr(p, '.');
                        if (p2)
                        {
                            char szName[256] = { 0 };
                            memcpy(szName, p + 1, p2 - p - 1);
                            if (strcmp(szName, szRoot) != 0)
                            {
                                if (!bFound && CompareName(szRoot, szName) < 0)
                                {
                                    fprintf(pOut, "<a href = \"%s\\%s.htm\" name = \"%s\">%s. %s</a>%s<br>\n", pDir, szRoot, szRoot, szRoot, szGlobalShortTitle, szDateStr);
                                    bFound = TRUE;
                                }
                                fprintf(pOut, szLine);
                            }
                            else
                            {
                                bFound = TRUE;
                                fprintf(pOut, "<a href = \"%s\\%s.htm\" name = \"%s\">%s. %s</a>%s<br>\n", pDir, szRoot, szRoot, szRoot, szGlobalShortTitle, szDateStr);
                            }
                            strcpy(szLastName, szName);
                        }
                        else
                            fprintf(pOut, "%s", szLine);
                    }
                    else
                        fprintf(pOut, "%s", szLine);

                }

            }
            if (!bFound)
            {
                fprintf(pOut, "<a href = \"%s\\%s.htm\" name = \"%s\">%s. %s</a>%s<br>\n", pDir, szRoot, szRoot, szRoot, szGlobalShortTitle, szDateStr);
            }

            fclose(pOut);

        }
        fclose(pIn);
        DeleteFile("..\\..\\index.htm");
        MoveFile("..\\..\\indext.htm", "..\\..\\index.htm");
    }
}

void DoStartIndex()
{
    FILE* pFile = fopen("..\\index.htm", "wb");
    if (pFile)
    {
        FILE* pFile1 = fopen("indexhead.txt", "rb");
        if (pFile1)
        {
            fseek(pFile1, 0, SEEK_END);
            int nSize = ftell(pFile1);
            fseek(pFile1, 0, SEEK_SET);
            if (nSize > 0)
            {
                char *szBuffer = new char[nSize];
                if (szBuffer)
                {
                    fread(szBuffer, nSize, 1, pFile1);
                    fwrite(szBuffer, nSize, 1, pFile);
                    delete[] szBuffer;
                }
            }
            fclose(pFile1);
        }
        fclose(pFile);
    }
}

void DoEndIndex()
{
    FILE* pFile = fopen("..\\index.htm", "ab");
    if (pFile)
    {
        FILE* pFile1 = fopen("indextail.txt", "rb");
        if (pFile1)
        {
            fseek(pFile1, 0, SEEK_END);
            int nSize = ftell(pFile1);
            fseek(pFile1, 0, SEEK_SET);
            if (nSize > 0)
            {
                char *szBuffer = new char[nSize];
                if (szBuffer)
                {
                    fread(szBuffer, nSize, 1, pFile1);
                    fwrite(szBuffer, nSize, 1, pFile);
                    delete[] szBuffer;
                }
            }
            fclose(pFile1);
        }
        fclose(pFile);
    }
}


void DoSlideShow(char *szPath, int bNeg)
{
    FILE* pFile = fopen(bNeg ? "slidesn.sll" : "slides.sll", "w");
    if (pFile)
    {
        for (int i = 0, iStart = 0; i < nFiles; i++)
        {
            int nFile = (bReverse) ? nFiles - i - 1 : i;

            int nLen = strlen(szFileNames[nFile]);
            if (nLen > 2 && stricmp(&szFileNames[nFile][nLen - 2], "!!") == 0)
            {
                char szTmp[_MAX_PATH];
                strcpy(szTmp, szFileNames[nFile]);
                szTmp[nLen - 2] = 0;
                fprintf(pFile, "%s\\Negatives\\%s\n", ".", szTmp);
            }
            else
            {
                if (!bNeg)
                    fprintf(pFile, "%s\\%s\n", ".", szFileNames[nFile]);
                else
                    fprintf(pFile, "%s\\Negatives\\%s\n", ".", szFileNames[nFile]);
            }


        }
        fclose(pFile);
    }

}

int Squash(char **szFileNames)
{
    for (int i = 1; i < nFiles; i++)
    {
        int nLen = strlen(szFileNames[i]);
        if (nLen > 2 && stricmp(&szFileNames[i][nLen - 2], "!!") == 0 &&
            strnicmp(szFileNames[i - 1], szFileNames[i], nLen - 2) == 0)
        {
            for (int j = i; j < nFiles - 1; j++)
            {
                szFileNames[j] = szFileNames[j + 1];
            }
            nFiles--;
        }
    }

    return nFiles;
}

void RenameSort(char **szFileNames, char *szPrefix)
{
    char szNewName[_MAX_PATH];
    int i;

    bSortByTime = TRUE;

    printf("renaming and sorting files\n");

    qsort(szFileNames, nFiles, sizeof(char *), compare);

    for (i = 0; i < nFiles; i++)
    {
        sprintf(szNewName, "xxx%s-%d.jpg", szPrefix, i + 1);
        if (MoveFile(szFileNames[i], szNewName))
            strcpy(szFileNames[i], szNewName);
    }
    for (i = 0; i < nFiles; i++)
    {
        sprintf(szNewName, "%s-%03d.jpg", szPrefix, i + 1);
        if (MoveFile(szFileNames[i], szNewName))
            strcpy(szFileNames[i], szNewName);
    }

}

void CreateMainPage(const char *szRoot, char *szPath, BOOL bNeg)
{
    char szNeg[2] = "";
    char szDate[16] = "";
    char szCurr[256];
    GetCurrentDirectory(255, szCurr);

    if (bNeg)
        strcpy(szNeg, "n");


    Squash(szFileNames);

    if (bSlideshow)
    {
        DoSlideShow(szPath, bNeg);
        return;
    }

    char szFileName[256];
    sprintf(szFileName, "%s%s.htm", szRoot, szNeg);
    FILE *pFile = fopen(szFileName, "w");
    if (pFile == NULL)
    {
        printf("Unable to create file %s", szFileName);
        return;
    }


    fprintf(pFile, 
        "<html>\n"
        "   <head>\n"
        "       <title>%s</title>\n"
        "       <LINK href=\"../main.css\" type=text/css rel=stylesheet>\n"
        "   </head>\n"
        "   <body>\n"
        , szGlobalShortTitle);

    if (pPrev && pPrev[0] != 0)
    {
        if (strcmp(pPrev, "x") != 0)
            fprintf(pFile, 
        "       <p>\n"
                    "<a href=\"%s\">%s</a> \n", pPrev, szPrevRoll);
    }
    else if (!bAuto)
        fprintf(pFile, 
        "       <p>\n"
        "           <a href=\"../%d/%d.htm\">%s</a> \n", atoi(szRoot) - 1, atoi(szRoot) - 1, szPrevRoll);

    if (pNext && pNext[0] != 0)
    {
        if (strcmp(pNext, "x") != 0)
            fprintf(pFile, 
        "           <a href=\"%s\">%s</a> \n", pNext, szNextRoll);
    }
    else if (!bAuto)
        fprintf(pFile, 
        "           <a href=\"../%d/%d.htm\">%s</a> \n", atoi(szRoot) + 1, atoi(szRoot) + 1, szNextRoll);

    if (bDoNegatives)
    {
        if (!bNeg)
            fprintf(pFile, 
        "           <a href=\"%sn.htm\">Negatives</a> \n", szRoot);
        else
            fprintf(pFile, 
        "           <a href=\"%s.htm\">Positives</a> \n", szRoot);
    }


    char szIndex[256] = "../../index.htm";
    WIN32_FIND_DATA data;
    HANDLE hFind = FindFirstFile("..\\..\\index.htm", &data);
    if (hFind == INVALID_HANDLE_VALUE)
    {
        strcpy(szIndex, "../../../index.htm");
    }
    else
        FindClose(hFind);

    char szDateStr[256] = "";
    if (bDoDate && szMinTaken[0] != 0 && szMaxTaken[0] != 0 && atoi(szMinTaken) != 0 && atoi(szMaxTaken) != 0)
    {
        if (CompareDate(szMinTaken, szMaxTaken) == 0)
            sprintf(szDateStr, 
        "           <font size=\"1\" face=\"Comic Sans MS\"> (%s)</font>\n", szMinTaken);
        else
            sprintf(szDateStr, 
        "           <font size=\"1\" face=\"Comic Sans MS\"> (%s to %s)</font>\n", szMinTaken, szMaxTaken);
    }

    if (!bLes)
    {
        fprintf(pFile,
        "           <a href=\"../index.htm\">CD Index</a> \n"
        "           <a href=\"%s\">Full Index</a> \n"
        "           Click any image to see a larger version\n"
        "       </p>\n"
        "       <p>\n"
        "           <strong>%s</strong>%s\n"
        "       </p>\n"
        "       <table border=\"1\" cellspacing=\"1\" width=\"624\">\n", szIndex, szGlobalTitle, szDateStr);
    }


    char szName[256];

    IThumb(szRoot, bNeg);

    for (int i = 0, iStart = 0; i < nFiles; i++)
    {
        if (i % nCols == 0)
        {
            fprintf(pFile, 
    "               <tr>\n");
            iStart = i;
        }

        int nFile = (bReverse) ? nFiles - i - 1 : i;

        _splitpath(szFileNames[nFile], 0, 0, szName, 0);
        char szThumb[128];
        if (!bLes)
            sprintf(szThumb, ThumbsFolderSlash"%s/%sth_%s", szRoot, szNeg, szFileNames[nFile]);
        else
            sprintf(szThumb, "./htm/th%s", szFileNames[nFile]);


        unsigned int nWidth = nThumbWidth, nHeight = nThumbHeight;
//        IThumb(szFileNames[nFile], szThumb, nThumbWidth, nThumbHeight, &nWidth, &nHeight, bThumb, bSmooth, szRoot, bNeg);
        char szTitle[256] = "";

        if (bDoDate)
        {
            GetTakenDate(szFileNames[nFile], szDate);
            if (szDate[0] != 0)
                sprintf(szTitle, "title=%s", szDate);
        }


        fprintf(pFile,
        "               <td width=\"17%%\">\n"
        "                   <a href=\"htm/%s%s.htm\"><img src=\"%s\" border=\"0\"  %s></a>\n"
        "               </td>\n",

            szNeg, szName, szThumb, szTitle);


        if (bReverse)
            CreateSubPage(szFileNames[nFile], szName, szRoot,
            (nFile < nFiles - 1) ? szFileNames[nFile + 1] : szFileNames[0], (nFile > 0) ? szFileNames[nFile - 1] : szFileNames[nFiles - 1], nFile, "", FALSE, bNeg);
        else
            CreateSubPage(szFileNames[nFile], szName, szRoot, (i > 0) ? szFileNames[i - 1] : szFileNames[nFiles - 1],
            (i < nFiles - 1) ? szFileNames[i + 1] : szFileNames[0], i, "", FALSE, bNeg);

        if ((i + 1) % nCols == 0 || i == nFiles - 1)
        {
            fprintf(pFile, 
        "           </tr>\n"
        "           <tr>\n");
            for (int j = iStart; j <= i; j++)
            {
                nFile = (bReverse) ? nFiles - j - 1 : j;
                _splitpath(szFileNames[nFile], 0, 0, szName, 0);

                char szTitle[256];
                int n = GetFileTitle(szFileNames[nFile], szTitle);
                char *pShort = GetShortTitle(szTitle);

                if (pShort && pShort[0] != 0)
                    fprintf(pFile,
        "               <td width=\"17%%\">\n"
        "                   %s\n"
        "               </td>\n",
                        pShort);
                else
                    fprintf(pFile,
        "               <td width=\"17%%\">\n"
        "                   %s\n"
        "               </td>\n", szTitle);
            }
            fprintf(pFile, 
        "           </tr>\n");
        }


    }

    fprintf(pFile, 
        "       </table>\n"
        "       <p></p>\n"
        "       <p>\n");
    if (!bNoMissing)
    {
        if (FindMissing(pFile, szBlank) > 0)
            fprintf(pFile, 
        "           Known to be blank\n"
        "       </p>\n"
        "       <p>");

        if (FindMissing(pFile, szMissing) > 0)
            fprintf(pFile, 
        "           Known to be missing\n"
        "       </p>"
        "       <p>");

        if (FindMissing(pFile, szDuplicate) > 0)
            fprintf(pFile, "Known to be duplicate</p><p>");

        if (FindMissing(pFile, NULL) > 0)
            fprintf(pFile, "Missing</p><p>");
    }

    fprintf(pFile, 
        "       </p>\n"
        "   </body>\n"
        "</html>\n");
    fclose(pFile);

}

void DoHtmlFile(char *szFile)
{
    FILE *pInFile = fopen(szFile, "r");
    if (pInFile == NULL)
    {
        printf("Unable to open file %s", szFile);
        return;
    }

    char szRoot[256], szDrive[256], szPath[256], szExt[32];
    _splitpath(szFile, szDrive, szPath, szRoot, 0);
    SetCurrentDirectory(szPath);


    WIN32_FIND_DATA data;
    HANDLE hFind = FindFirstFile("htm\\*.*", &data);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        system("del htm  /q");
        FindClose(hFind);
    }

    CreateDirectory("htm", NULL);

    char szFileName[256];
    sprintf(szFileName, "%s%s%s.htm", szDrive, szPath, szRoot);

    FILE *pOutFile = fopen(szFileName, "w");
    if (pOutFile == NULL)
    {
        printf("Unable to create file %s", szFileName);
        return;
    }

    fprintf(pOutFile,
        "<html>\n"
        "<head><title>%s</title><LINK href=\"../main.css\" type=text/css rel=stylesheet></head>\n"
        "<body>\n"
        "<a href=\"../index.htm\">Home</a>", szGlobalShortTitle);

    if (szFull)
        fprintf(pOutFile,
            " <a href=\"%s\">Full</a>", szFull);

    fprintf(pOutFile,
        " Click any image to see a larger version</p><p><strong>%s</strong></p>\n"
        "<table border=\"1\" cellspacing=\"1\" width=\"624\">\n",
        szGlobalTitle);

    char szName[256];

    nFiles = 0;
    while (fgets(szName, 255, pInFile))
    {
        char *pName = szName;
        while (isspace((unsigned char)*pName))
            pName++;

        if (strlen(pName) > 0)
            nFiles++;
    }
    fseek(pInFile, 0, SEEK_SET);
    szFileNames = new char*[nFiles];

    int nFile = 0;
    while (fgets(szName, 255, pInFile))
    {
        char *pName = szName;
        while (isspace((unsigned char)*pName))
            pName++;

        while (strlen(pName) > 0 && isspace((unsigned char)pName[strlen(pName) - 1]))
            pName[strlen(pName) - 1] = 0;


        if (strlen(pName) > 0)
        {
            szFileNames[nFile] = new char[strlen(pName) + 1];
            strcpy(szFileNames[nFile], pName);
            nFile++;
        }
    }
    fclose(pInFile);

    IThumb(szRoot, false);


    for (int i = 0, iStart = 0; i < nFiles; i++)
    {
        if (i % nCols == 0)
        {
            fprintf(pOutFile, "<tr>\n");
            iStart = i;
        }

        int nFile = (bReverse) ? nFiles - i - 1 : i;

        _splitpath(szFileNames[nFile], szDrive, szPath, szName, szExt);
        int nLen = strlen(szPath);
        if (nLen > 0 && (szPath[nLen - 1] == '/' || szPath[nLen - 1] == '\\'))
            szPath[--nLen] = 0;

        char szNewPath[256];
        sprintf(szNewPath, "../%s", szPath);
        ReadTitles(szNewPath, szName, (szTitlesFile) ? szTitlesFile : "titles.txt");

        char szThumb[128];
        sprintf(szThumb, ThumbsFolderSlash"%s/th_%s%s", szRoot, szName, szExt);

        unsigned int nWidth = nThumbWidth, nHeight = nThumbHeight;

        fprintf(pOutFile,
            "\t\t<td width=\"17%%\">\n"
            "\t\t\t<a href=\"htm/%s.htm\"><img src=\"%s\" border=\"0\"></a>\n"
            "\t\t</td>\n",szName, szThumb);

        sprintf(szNewPath, "../%s/", szPath);
        CreateSubPage(szFileNames[nFile], szName, szRoot, (i > 0) ? szFileNames[i - 1] : szFileNames[nFiles - 1],
            (i < nFiles - 1) ? szFileNames[i + 1] : szFileNames[0], i, szNewPath, TRUE, FALSE);

        if ((i + 1) % nCols == 0 || i == nFiles - 1)
        {
            fprintf(pOutFile, "\t</tr>\n\t<tr>\n");
            for (int j = iStart; j <= i; j++)
            {
                nFile = (bReverse) ? nFiles - j - 1 : j;
                char szFileName[256];
                int n = GetFileTitle(szFileNames[nFile], szFileName);

                _splitpath(szFileNames[nFile], szDrive, szPath, szName, szExt);
                sprintf(szNewPath, "../%s", szPath);
                ReadTitles(szNewPath, szName, (szShortFile) ? szShortFile : "short.txt");
                char *pShort = GetShortTitle(szFileName);

                if (pShort[0] != 0)
                    fprintf(pOutFile,
                        "\t\t<td width=\"17%%\">%s</td>\n",
                        pShort);
                else
                    fprintf(pOutFile,
                        "\t\t<td width=\"17%%\">%s</td>\n", szFileName);

            }
            fprintf(pOutFile, "\t</tr>\n");
        }
    }

    fprintf(pOutFile, "</table>\n</body>\n</html>\n");
    fclose(pOutFile);
}

void DoHtmlFolder(char *szFolder)
{
    char szRoot[256];
    _splitpath(szFolder, 0, 0, szRoot, 0);

    szMinTaken[0] = 0;
    szMaxTaken[0] = 0;

    printf("Making album from %s\n", szFolder);
    if (!SetCurrentDirectory(szFolder))
    {
        printf("Unable to change to folder %s\n", szFolder);
        return;
    }
    GetCurrentDirectory(255, szFolder);


    WIN32_FIND_DATA data;
    HANDLE hFind;
    hFind = FindFirstFile("Negatives\\*.jpg", &data);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        FindClose(hFind);
        bDoNegatives = bAllowNegatives;
    }
    else
        bDoNegatives = FALSE;


    nFiles = ScanFiles("*.jpg", szFolder, FALSE);
    if (nFiles == 0)
        return;
    qsort(szFileNames, nFiles, sizeof(char *), compare);
    ReadTitles(szFolder, szRoot, (szTitlesFile) ? szTitlesFile : "titles.txt");

    char szFileName[256];
    sprintf(szFileName, "%s.htm", szRoot);
    DoIndexAuto(szRoot, szFolder);

    BOOL bSkip = FALSE;

    if (bAuto)
    {
        WIN32_FIND_DATA data1;
        char szSearch[256];
        HANDLE hFile1;

        if (bLes)
            sprintf(szSearch, ".\\htm\\th*.jpg");
        else
            sprintf(szSearch, ThumbsFolderBackslash"%s\\*.jpg", szRoot);

        hFile1 = FindFirstFile(szSearch, &data1);
        if (hFile1 != INVALID_HANDLE_VALUE)
        {
            FindClose(hFile1);
            hFile1 = FindFirstFile(szFileName, &data1);

            if (hFile1 != INVALID_HANDLE_VALUE)
            {
                WIN32_FIND_DATA data2;
                HANDLE hFile2 = INVALID_HANDLE_VALUE;
                if (szDriveTitles1[0] != 0)
                {
                    char szTitles[256];
                    sprintf(szTitles, "%s\\%s\\%s\\titles.txt", szDriveTitles1, pRootFolder, szRoot);
                    hFile2 = FindFirstFile(szTitles, &data2);
                }
                if (hFile2 == INVALID_HANDLE_VALUE && szDriveTitles2[0] != 0)
                {
                    char szTitles[256];
                    sprintf(szTitles, "%s\\%s\\%s\\titles.txt", szDriveTitles2, pRootFolder, szRoot);
                    hFile2 = FindFirstFile(szTitles, &data2);
                }

                if (hFile2 == INVALID_HANDLE_VALUE)
                    hFile2 = FindFirstFile("titles.txt", &data2);

                if (hFile2 != INVALID_HANDLE_VALUE)
                {
                    if (CompareFileTime(&data1.ftLastWriteTime, &data2.ftLastWriteTime) > 0 && bDoSkip)
                        bSkip = TRUE;
                    FindClose(hFile2);
                }
                FindClose(hFile1);
            }
        }

        if (bSkip && !bThumb)
            return;
    }


    if (bDoIndex)
    {
        DoIndex(szRoot, szFolder);
        return;
    }


    char szThumDest[256];
    if (!bLes)
        sprintf(szThumDest, ThumbsFolderBackslash"%s", szRoot);
    else
        sprintf(szThumDest, ".\\htm\\");

    CreateDirectory(ThumbsFolderBackslash, NULL);
    CreateDirectory(szThumDest, NULL);

    if (!SetCurrentDirectory(szThumDest))
    {
        printf("Unable to change to folder %s\n", szThumDest);
        return;
    }
    else if (bThumb & !bLes)
    {
        system("del th*.jpg /q");
    }

    SetCurrentDirectory(szFolder);
    sprintf(szThumDest, ".\\thumb");

    if (SetCurrentDirectory(szThumDest) && bThumb)
        system("del *.* /q");

    SetCurrentDirectory(szFolder);

    hFind = FindFirstFile("..\\..\\..\\htm\\*.*", &data);
    if (hFind != INVALID_HANDLE_VALUE && !bSlideshow)
    {
        system("del htm /q");
        FindClose(hFind);
    }




    hFind = FindFirstFile("*.htm", &data);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        system("del *.htm /q");
        FindClose(hFind);
    }

    hFind = FindFirstFile("Th*.db", &data);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        system("del Th*.db /q /f /A:H");
        FindClose(hFind);
    }

    hFind = FindFirstFile("Negatives\\Th*.db", &data);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        system("del Negatives\\Th*.db /q /f /A:H");
        FindClose(hFind);
    }

    CreateDirectory("htm", NULL);

    if (!SetCurrentDirectory("htm"))
    {
        printf("Unable to create folder htm\n");
        return;
    }
    SetCurrentDirectory(szFolder);

    CreateMainPage(szRoot, szFolder, FALSE);
    if (bDoNegatives)
        CreateMainPage(szRoot, szFolder, TRUE);
}

void RemoveTags(char *pIn, char *pOut)
{
    int nLen = strlen(pIn);
    int i, j;

    for (i = 0, j = 0; i < nLen; i++)
    {
        if (pIn[i] == '<')
        {
            if (strnicmp(&pIn[i], "<br>", 4) == 0)
            {
                pOut[j] = 0;
                return;
            }
            else
            {
                i++;
                while (pIn[i] && pIn[i] != '>')
                    i++;
            }
        }
        else
        {
            pOut[j++] = pIn[i];
        }
    }
    pOut[j] = 0;
}

void RemoveForeign(char *pIn)
{
    int nLen = strlen(pIn);
    int i, j;
    char szOut[TITLE_LEN] = "";
    char *pOut = szOut;

    for (i = 0, j = 0; i < nLen; i++)
    {
        if (pIn[i] == 'ß')
        {
            pOut[j++] = 's';
            pOut[j++] = 's';
        }
        else if (pIn[i] == 'ä')
        {
            pOut[j++] = 'a';
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'Ä')
        {
            pOut[j++] = 'A';
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'ö')
        {
            pOut[j++] = 'o';
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'Ö')
        {
            pOut[j++] = 'O';
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'ü')
        {
            pOut[j++] = 'u';
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'Ü')
        {
            pOut[j++] = 'U';
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'á')
        {
            pOut[j++] = 'a';
        }
        else if (pIn[i] == 'Á')
        {
            pOut[j++] = 'A';
        }
        else if (pIn[i] == 'é')
        {
            pOut[j++] = 'e';
        }
        else if (pIn[i] == 'É')
        {
            pOut[j++] = 'E';
        }
        else if (pIn[i] == 'í')
        {
            pOut[j++] = 'i';
        }
        else if (pIn[i] == 'Í')
        {
            pOut[j++] = 'I';
        }
        else if (pIn[i] == 'ó')
        {
            pOut[j++] = 'o';
        }
        else if (pIn[i] == 'ñ')
        {
            pOut[j++] = 'n';
        }
        else if (pIn[i] == 'Ñ')
        {
            pOut[j++] = 'N';
        }
        else if (pIn[i] == 'Ó')
        {
            pOut[j++] = 'o';
        }
        else if (pIn[i] == 'ú')
        {
            pOut[j++] = 'u';
        }
        else if (pIn[i] == 'Ú')
        {
            pOut[j++] = 'U';
        }
        else if (pIn[i] == '\"' || (unsigned char)pIn[i] > 126)
        {
            // Skip
        }
        else
        {
            pOut[j++] = pIn[i];
        }
    }
    strcpy(pIn, pOut);
}

void DoExifFolder(char *szFolder, bool bRemoveOrientation)
{
    char szRoot[256];
    char szCurr[256];

    _splitpath(szFolder, 0, 0, szRoot, 0);

    printf("Updating exif info in %s\n", szFolder);
    if (!bRemoveOrientation && !SetCurrentDirectory(szFolder))
    {
        printf("Unable to change to folder %s\n", szFolder);
        return;
    }
    GetCurrentDirectory(255, szCurr);

    if (bRemoveOrientation)
    {
        char szCmd[1024];
        sprintf(szCmd, "exiftool -Orientation= \"%s\"", szFolder);
        printf("%s\n", szCmd);
        fflush(stdout);
        system(szCmd);
        return;
    }

    nFiles = ScanFiles("*.jpg", szCurr, FALSE);
    if (nFiles == 0)
        return;
    qsort(szFileNames, nFiles, sizeof(char *), compare);



    ReadTitles(szFolder, szRoot, (szTitlesFile) ? szTitlesFile : "titles.txt");


    for (int i = 0; i < nFiles; i++)
    {
        char szName[1024];
        int n = GetFileTitle(szFileNames[i], szName);

        char *pShort = GetTextTitle(szName);
        char szCmd[1024];
        char szTitle[1024], szCaption[1024];

        RemoveTags(szGlobalTitle, szTitle);
        RemoveTags(pShort, szCaption);

        RemoveForeign(szTitle);
        RemoveForeign(szCaption);

        if (strlen(szTitle) > 0)
        {
            sprintf(szCmd, "exiftool -Title=\"%s\" -overwrite_original \"%s\"", szTitle, szFileNames[i]);
            printf("%s\n", szCmd);
            fflush(stdout);
            system(szCmd);
        }
        if (strlen(szCaption) > 0)
        {
            sprintf(szCmd, "exiftool -Caption-Abstract=\"%s\"  -overwrite_original \"%s\"", szCaption, szFileNames[i]);
            printf("%s\n", szCmd);
            fflush(stdout);
            system(szCmd);
            sprintf(szCmd, "exiftool -Subject=\"%s\" -overwrite_original  \"%s\"", szCaption, szFileNames[i]);
            printf("%s\n", szCmd);
            fflush(stdout);
            system(szCmd);
        }
    }


    SetCurrentDirectory(szFolder);
}

void CrunchFiles(char *szFolder, char *szOutFile, unsigned int nX = 4, unsigned int nY = 3)
{
    char szHome[256];
    GetCurrentDirectory(256, szHome);
    if (SetCurrentDirectory(szFolder))
    {
        nFiles = ScanFiles("*.jpg", szFolder, TRUE);
        BYTE *pData = new BYTE[nX * nY * 3 * nFiles];
        memset(pData, 0, nX * nY * 3 * nFiles);
        if (pData)
        {
            FILE *pFile = fopen(szOutFile, "wb");
            if (pFile)
            {
                fprintf(pFile, "%05d%03d%03d", nFiles, nX, nY);
                printf("Creating crunch file %s at resolution %d x %d\n",
                    szOutFile, nX, nY);
                for (int n = 0; n < nFiles; n++)
                {
                    unsigned int nScale = 1; ;
                    BYTE *p1 = Normalise(szFileNames[n], nX, nY, &nScale, TRUE, TRUE, TRUE);
                    if (p1)
                    {
                        memcpy(&pData[nX * nY * 3 * n], p1, nX * nY * 3);
                        fprintf(pFile, "%03d%s", strlen(szFileNames[n]), szFileNames[n]);
                        delete[] p1;
                    }
                    else
                        fprintf(pFile, "%03d", 0);
                    printf("%d of %d\r", n + 1, nFiles);

                }
                fwrite(pData, nX * nY * 3 * nFiles, 1, pFile);
                fclose(pFile);
                printf("\n");
            }
        }

    }
    SetCurrentDirectory(szHome);
}


BYTE * ReadCrunchFile(char *szInFile, int &nX, int &nY)
{
    FILE *pFile = fopen(szInFile, "rb");
    BYTE *pRet = NULL;
    if (pFile)
    {
        fseek(pFile, 0, SEEK_END);
        int nSize = ftell(pFile);
        fseek(pFile, 0, SEEK_SET);
        BYTE *pBuffer = new BYTE[nSize];
        if (pBuffer)
        {
            fread(pBuffer, nSize, 1, pFile);
            char sznFiles[6] = { 0 }, sznX[4] = { 0 }, sznY[4] = { 0 };
            memcpy(sznFiles, pBuffer, 5);
            memcpy(sznX, pBuffer + 5, 3);
            memcpy(sznY, pBuffer + 8, 3);
            nFiles = atoi(sznFiles);
            nX = atoi(sznX);
            nY = atoi(sznY);
            BYTE *ptr = pBuffer + 11;
            szFileNames = new char*[nFiles];

            for (int n = 0; n < nFiles; n++)
            {
                char sznLen[4] = { 0 };
                memcpy(sznLen, ptr, 3);
                int nLen = atoi(sznLen);

                szFileNames[n] = new char[nLen + 2];
                if (nLen > 0)
                    memcpy(szFileNames[n], ptr + 3, nLen);

                szFileNames[n][nLen] = 0;
                szFileNames[n][nLen + 1] = 0;


                ptr += nLen + 3;
            }

            pRet = new BYTE[nSize - (ptr - pBuffer)];
            if (pRet)
                memcpy(pRet, ptr, nSize - (ptr - pBuffer));
            delete[]pBuffer;
        }
        fclose(pFile);
    }
    return pRet;
}


char * Match(const BYTE *pData, BYTE *pTmp, int nX, int nY)
{
    char *pBest = NULL;
    int i, n;
    if (nTop < 1)
        nTop = 1;

    int *nBestFit = new int[nTop];
    if (nBestFit)
    {
        int *nBestFile = new int[nTop];
        if (nBestFile)
        {
            int nFound = 0;

            for (n = 0; n < nTop; n++)
            {
                nBestFit[n] = nX * nY * 3 * 255;
                nBestFile[n] = 0;
            }

            for (i = 0; i < nFiles; i++)
            {

                if (szFileNames[i][0] != 0 && (!bUnique || szFileNames[i][strlen(szFileNames[i]) + 1] == 0))
                {
                    int nFit = 0, j;
                    for (j = 0; j < nX*nY * 3; j++)
                    {
                        nFit += abs(pData[i*nX*nY * 3 + j] - pTmp[j]);
                    }
                    for (j = 0; j < nTop; j++)
                    {
                        if (nFit < nBestFit[j])
                        {
                            nFound++;
                            for (n = nTop - 1; n > j; n--)
                            {
                                nBestFit[n] = nBestFit[n - 1];
                                nBestFile[n] = nBestFile[n - 1];
                            }

                            nBestFit[j] = nFit;
                            nBestFile[j] = i;
                            break;
                        }
                    }
                }
            }

            if (nFound > 0)
            {
                int nRand = rand() % min(nFound, nTop);
                pBest = szFileNames[nBestFile[nRand]];

                for (i = 0; i < nX*nY * 3; i++)
                    pTmp[i] = pData[nBestFile[nRand] * nX*nY * 3 + i];

                pBest[strlen(pBest) + 1] = 1;
            }
            delete[] nBestFile;
        }
        delete[] nBestFit;
    }

    return pBest;
}

void Pixellate(char *szInFile, char *szOutFile, unsigned int nBlocks, unsigned int nPixelsPerBlock, BOOL bCopy)
{
    char szImageDir[256], szImageFiles[256], szCmd[256], szImageFile[256];
    strcpy(&szImageDir[1], szOutFile);
    szImageDir[0] = '~';
    int n;

    char *ptr = strrchr(szImageDir, '.');
    if (ptr)
        *ptr = 0;

    sprintf(szImageFile, "%s\\%s", szImageDir, szOutFile);
    sprintf(szImageFiles, "%s\\*.jpg", szImageDir);
    sprintf(szCmd, "del %s\\*.jpg /q", szImageDir);
    CreateDirectory(szImageDir, NULL);

    if (bCopy)
    {
        WIN32_FIND_DATA data;
        HANDLE hFind = FindFirstFile("szImageDir\\*.jpg", &data);
        if (hFind != INVALID_HANDLE_VALUE)
        {
            system(szCmd);
            FindClose(hFind);
        }
    }

    srand(GetTickCount());
    int nX, nY;
    unsigned int nScale;
    char szHtmFile[256];
    sprintf(szHtmFile, "%s\\%s", szImageDir, szOutFile);
    ptr = strrchr(szHtmFile, '.');
    if (ptr)
        strcpy(ptr, ".htm");
    else
        strcat(ptr, ".htm");

    BYTE *pData = ReadCrunchFile(szCrunchFile, nX, nY);

    if (pData)
    {
        unsigned int nOrigX = nBlocks * nX;
        unsigned int nOrigY = nOrigX * nY / nX;

        unsigned int nNewX = nOrigX * nPixelsPerBlock / nX;
        unsigned int nNewY = nNewX * nY / nX;

        unsigned int nSmallX = nPixelsPerBlock;
        unsigned int nSmallY = nSmallX * nY / nX;

        BYTE *pTmp = new BYTE[nX*nY * 3];
        if (pTmp)
        {
            BYTE *p1 = Normalise(szInFile, nOrigX, nOrigY, &nScale, TRUE, TRUE);

            if (p1)
            {
                BYTE *pNew = new BYTE[nNewX*nNewY * 3];
                if (pNew)
                {
                    FILE *pHtmFile = fopen(szHtmFile, "w");
                    if (pHtmFile)
                    {
                        fprintf(pHtmFile,
                            "<html>\n<title>%s</title>\n<body>\n"
                            "<img src=\"%s\" width=\"%d\" height=\"%d\" usemap=\"#Map\">\n"
                            "  <map name=\"Map\">",
                            szHtmFile, szOutFile, nNewX, nNewY
                        );


                        for (unsigned int y = 0; y < nOrigY; y += nY)
                        {
                            for (unsigned int x = 0, x1 = 0; x < nOrigX * 3; x += 3 * nX, x1 += nSmallX * 3)
                            {
                                for (n = 0; n < nY; n++)
                                {
                                    memcpy(pTmp + n * nX * 3, p1 + x + (y + n)*nOrigX * 3, nX * 3);
                                }
                                char *szMatch = Match(pData, pTmp, nX, nY);
                                if (szMatch)
                                {
                                    char szNewFile[256];
                                    if (bCopy)
                                    {
                                        char * ptr = strrchr(szMatch, '/');
                                        if (ptr)
                                            sprintf(szNewFile, "%s%s", szImageDir, ptr);
                                        else
                                            sprintf(szNewFile, "%s/%s", szImageDir, szMatch);
                                        CopyAFile(szMatch, szNewFile, FALSE);
                                    }
                                    else
                                        sprintf(szNewFile, "../%s", szMatch);

                                    BYTE *p2 = Normalise(szMatch, nSmallX, nSmallY, &nScale, TRUE, TRUE);
                                    if (p2)
                                    {
                                        for (unsigned int y1 = 0; y1 < nSmallY; y1++)
                                            memcpy(pNew + (y / nY * nSmallY + y1)*nNewX * 3 + x1,
                                                p2 + y1 * nSmallX * 3, nSmallX * 3);
                                        delete[] p2;
                                    }

                                    for (n = 0; n < nY; n++)
                                    {
                                        memcpy(p1 + x + (y + n)*nOrigX * 3, pTmp + n * nX * 3, nX * 3);
                                    }
                                    char *szImg = strrchr(szNewFile, '//');
                                    if (!bCopy || szImg == NULL)
                                        szImg = szNewFile;
                                    else
                                        szImg++;
                                    fprintf(pHtmFile, "     <area shape=\"rect\" coords=\"%d,%d,%d,%d\" href=\"%s\" >\n",
                                        x1 / 3, y / nY * nSmallY, x1 / 3 + nSmallX, y / nY * nSmallY + nSmallY, szImg);

                                }
                                printf("%5d,%5d of %5d,%5d\r", x / 3 / nX, y / nY, nOrigX / nX, nOrigY / nY);
                            }
                        }
                        JpegFile::RGBToJpegFile(szImageFile, pNew, nNewX, nNewY, TRUE, 50);
                        //delete [] pNew ;
                        fprintf(pHtmFile, "  </map></body></html>\n");
                        fclose(pHtmFile);
                    }
                }

                delete[] p1;
            }
            delete[] pTmp;
        }
        delete[] pData;
    }
    printf("\n");
}

void DoFavourites(char *szFavName)
{
    char pFavourites[128];
    char pHtml[128];

    sprintf(pFavourites, "..\\%s.txt", szFavName);
    sprintf(pHtml, "%s.htm", szFavName);

    FILE *pIn = fopen(pFavourites, "r");
    if (pIn)
    {
        FILE *pOut = fopen(pHtml, "w");
        if (pOut)
        {
            char szFile[_MAX_PATH], szTitle[MAX_TITLE_LEN], szLine[MAX_TITLE_LEN], szTmpLine[MAX_TITLE_LEN], szHeading[MAX_TITLE_LEN] = "", szHtm[_MAX_PATH];
            int nIndex = 0;
            while (fgets(szLine, MAX_TITLE_LEN, pIn))
            {
                char szName[_MAX_PATH] = "th";
                unsigned int nWidth = FAV_THUMB_WIDTH, nHeight = FAV_THUMB_HEIGHT;
                int nLen = strlen(szLine);
                for (; nLen > 0 && isspace((unsigned char)szLine[nLen - 1]); nLen--)
                    szLine[nLen - 1] = 0;

                int nPos = ftell(pIn);
                while (fgets(szTmpLine, MAX_TITLE_LEN, pIn))
                {
                    nLen = strlen(szTmpLine);
                    for (; nLen > 0 && isspace((unsigned char)szTmpLine[nLen - 1]); nLen--)
                        szTmpLine[nLen - 1] = 0;
                    if (nLen != 0)
                        break;

                    nPos = ftell(pIn); // Skip blank lines
                }
                fseek(pIn, nPos, SEEK_SET);

                char *pJpg = strstr(szLine, ".jpg ");
                if (!pJpg)
                    pJpg = strstr(szLine, ".JPG ");
                if (pJpg)
                {
                    if (nIndex == 0)
                        fprintf(pOut, "<HTML><BODY>\n%s\n<table><tr>\n", szHeading);
                    nIndex++;
                    *(pJpg + 4) = 0;
                    strcpy(szFile, szLine);
                    FixFileName(szFile);
                    strcpy(szTitle, pJpg + 5);

                    sprintf(szName, "th%d.jpg", nIndex);
                    sprintf(szHtm, "%d.htm", nIndex);

                    Thumb(szFile, szName, nWidth, nHeight, &nWidth, &nHeight, TRUE, TRUE, "", FALSE);
                    fprintf(pOut, "<td><a href=\"%s\"><img src=\"%s\" border=\"0\" width=\"%d\"height=\"%d\"><br>%s</a></td>\n", szHtm, szName, nWidth, nHeight, szTitle);
                    if (nIndex % 6 == 0)
                    {
                        fprintf(pOut, "</tr><tr>\n");
                    }
                    nWidth = FAV_WIDTH; nHeight = nImgHeight;
                    Thumb(szFile, &szName[2], nWidth, nHeight, &nWidth, &nHeight, TRUE, TRUE, "", FALSE);
                    FILE *pHtm = fopen(szHtm, "w");
                    if (pHtm)
                    {
                        if (nIndex == 1)
                        {
                            fprintf(pHtm, "<HTML><BODY>\n<a href=\"%s.htm\">Back</a> <a href=\"%d.htm\">Next</a>  <table border=\"%d\">\n<caption align=\"bottom\">%s</Caption>\n<tr><td>\n<img src=\"%s\" height=\"%d\" width=\"%d\">\n</td></tr>\n</table>\n</BODY></HTML>\n",
                                szFavName, nIndex + 1, bMinutes ? 1 : 10, szTitle, &szName[2], nHeight, nWidth);
                        }
                        else if (szTmpLine[0] != 0)
                        {
                            fprintf(pHtm, "<HTML><BODY>\n<a href=\"%s.htm\">Back</a> <a href=\"%d.htm\">Next</a>  <a href=\"%d.htm\">Previous</a><table border=\"%d\">\n<caption align=\"bottom\">%s</Caption>\n<tr><td>\n<img src=\"%s\" height=\"%d\" width=\"%d\">\n</td></tr>\n</table>\n</BODY></HTML>\n",
                                szFavName, nIndex + 1, nIndex - 1, bMinutes ? 1 : 10, szTitle, &szName[2], nHeight, nWidth);
                        }
                        else
                        {
                            fprintf(pHtm, "<HTML><BODY>\n<a href=\"%s.htm\">Back</a> <a href=\"%d.htm\">Previous</a><table border=\"%d\">\n<caption align=\"bottom\">%s</Caption>\n<tr><td>\n<img src=\"%s\" height=\"%d\" width=\"%d\">\n</td></tr>\n</table>\n</BODY></HTML>\n",
                                szFavName, nIndex - 1, bMinutes ? 1 : 10, szTitle, &szName[2], nHeight, nWidth);
                        }



                        fclose(pHtm);
                    }

                }
                else if (nIndex == 0)
                {
                    strcpy(szHeading, szLine);
                }

            };
            fprintf(pOut, "</HTML></BODY>\n");
            fclose(pOut);
        }
        else
        {
            printf("Unable to open file %s", pHtml);
        }

        fclose(pIn);
    }
    else
    {
        printf("Unable to open file %s", pFavourites);
    }

}

void ScanTooSmall(char *szFolder, unsigned int nSize)
{
    char szHome[256];
    GetCurrentDirectory(256, szHome);
    printf("The following files are less than %d pixels high:\n", nSize);
    if (SetCurrentDirectory(szFolder))
    {
        nFiles = ScanFiles("*.jpg", szFolder, TRUE);
        for (int n = 0; n < nFiles; n++)
        {
            unsigned int nScale = 1; ;
            JpegFile jFile;
            unsigned int nWidth = 0, nHeight = 0;
            jFile.GetJPGDimensions(szFileNames[n], &nWidth, &nHeight);
            if (nHeight < nSize)
                printf("This file is %3dx%3d: %s\n", nWidth, nHeight, szFileNames[n]);
        }
    }
    SetCurrentDirectory(szHome);
}

int SortData(const void *arg1, const void *arg2)
{
    WIN32_FIND_DATA *data1 = *(WIN32_FIND_DATA **)arg1;
    WIN32_FIND_DATA *data2 = *(WIN32_FIND_DATA **)arg2;
    if (isdigit(data1->cFileName[0]) && isdigit(data2->cFileName[0]))
        return (atoi(data1->cFileName) - atoi(data2->cFileName));
    else if (isdigit(data1->cFileName[1]) && isdigit(data2->cFileName[1]) &&
        !isdigit(data1->cFileName[0]) && !isdigit(data2->cFileName[0]) &&
        data1->cFileName[0] == data2->cFileName[0])
        return (atoi(&data1->cFileName[1]) - atoi(&data2->cFileName[1]));
    else
        return strcmp(data1->cFileName, data2->cFileName);
}



void DoAuto()
{
    WIN32_FIND_DATA data;
    WIN32_FIND_DATA *datas[1000];

    HANDLE hFind = FindFirstFile("*.*", &data);
    char szThis[_MAX_PATH] = "";
    char szPrevious[_MAX_PATH] = "";
    char szNext[_MAX_PATH] = "";
    char szCurr[_MAX_PATH];
    BOOL bNext = FALSE;
    pPrev = szPrevious;
    pNext = szNext;
    FILE *pFile;
    int nDirs = 0;

    GetCurrentDirectory(_MAX_PATH, szCurr);
    pFile = fopen("main.css", "r");
    if (pFile)
    {
        fclose(pFile);
    }
    else
    {
        pFile = fopen("main.css", "w");
        if (pFile)
        {
            fprintf(pFile,
                "TD {"
                "    FONT-WEIGHT: normal; FONT-SIZE: 10px; TEXT-ALIGN:center; COLOR: darkblue; LINE-HEIGHT: 11px; FONT-STYLE: normal; FONT-FAMILY: Times New Roman\n"
                "}\n"
                "A {\n"
                "    COLOR: red; TEXT-DECORATION: none\n"
                "}\n"
                "a:link {\n"
                "    COLOR: blue; TEXT-DECORATION: underline\n"
                "}\n"
                "A:visited {\n"
                "    COLOR: purple; TEXT-DECORATION: underline\n"
                "}\n"
                "a:active {\n"
                "    COLOR: black; TEXT-DECORATION: underline\n"
                "}\n"
            );

            fclose(pFile);
        }
    }
    FILE *pfile = fopen("index.htm", "w");
    char *pRoot = strrchr(szCurr, '\\') + 1;
    if (pFile)
    {
        if (bLes)
            fprintf(pFile, "<html>\n<head>\n</head>\n<title>\nMap-Print Maps\n</title>\n<body>\n<h3>Map-Print Maps %s</h3>", pRoot);
        else
            fprintf(pFile, "<html>\n<head>\n</head>\n<title>\nMy Photographs\n</title>\n<body>\n<h3>My Photographs %s</h3>", pRoot);
    }

    FILE *pMain = fopen("..\\index.htm", "r");
    if (pMain)
    {
        fclose(pMain);
        if (!bLes)
            fprintf(pFile, "<p><a href=\"../index.htm\">Complete Index</a></p>\n");
        else
            fprintf(pFile, "<p><a href=\"http://www.map-print.net\">Main Index</a></p>\n");
    }
    do
    {
        if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) != 0
            && stricmp(data.cFileName, ".") != 0
            && stricmp(data.cFileName, "..") != 0)
        {
            SetCurrentDirectory(data.cFileName);
            WIN32_FIND_DATA data2;
            HANDLE hFind2 = FindFirstFile("*.jpg", &data2);
            SetCurrentDirectory(szCurr);
            if (hFind2 != INVALID_HANDLE_VALUE)
            {
                FindClose(hFind2);

                datas[nDirs] = new WIN32_FIND_DATA;
                if (datas[nDirs])
                    memcpy(datas[nDirs], &data, sizeof(data));
                nDirs++;
            }

            do
            {
                bNext = FindNextFile(hFind, &data);
            } while (bNext &&
                ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) == 0
                    || stricmp(data.cFileName, ".") == 0
                    || stricmp(data.cFileName, "..") == 0));

        }
        else
            bNext = FindNextFile(hFind, &data);

    } while (bNext);

    qsort(datas, nDirs, sizeof(void *), SortData);


    FindClose(hFind);

    if (nDirs > 0)
        sprintf(szPrevious, "../%s/%s.htm", datas[nDirs - 1]->cFileName, datas[nDirs - 1]->cFileName);
    for (int i = 0; i < nDirs; i++)
    {
        bReverse = FALSE;
        bDoDate = FALSE;
        SetCurrentDirectory(szCurr);
        strcpy(szThis, datas[i]->cFileName);
        strcpy(szFolder, datas[i]->cFileName);

        if (i < nDirs - 1)
            sprintf(szNext, "../%s/%s.htm", datas[i + 1]->cFileName, datas[i + 1]->cFileName);
        else
            sprintf(szNext, "../%s/%s.htm", datas[0]->cFileName, datas[0]->cFileName);


        szGlobalShortTitle[0] = 0;
        pPrev = szPrevious;
        pNext = szNext;
        DoHtmlFolder(szFolder);

        char szDateStr[256] = "";
        if (bDoDate && szMinTaken[0] != 0 && szMaxTaken[0] != 0 && atoi(szMinTaken) != 0 && atoi(szMaxTaken) != 0)
        {
            if (CompareDate(szMinTaken, szMaxTaken) == 0)
                sprintf(szDateStr, "<font size=\"1\" face=\"Comic Sans MS\"> (%s)</font>", szMinTaken);
            else
                sprintf(szDateStr, "<font size=\"1\" face=\"Comic Sans MS\"> (%s to %s)</font>", szMinTaken, szMaxTaken);
        }

        if (nFiles > 0)
        {
            if (pFile)
            {
                if (atoi(szThis) <= 0)
                    fprintf(pFile, "<a href = \"%s/%s.htm\" name = \"%s\">%s</a> %s<br>\n", szThis, szThis, szThis, szGlobalShortTitle, szDateStr);
                else
                    fprintf(pFile, "<a href = \"%s/%s.htm\" name = \"%s\">%d. %s</a> %s<br>\n", szThis, szThis, szThis, atoi(szThis), szGlobalShortTitle, szDateStr);

            }

            sprintf(szPrevious, "../%s/%s.htm", szThis, szThis);
            DeleteFileNames();
        }

    }

    if (pFile)
    {
        fprintf(pfile, "</body></html>");
        fclose(pFile);
    }

}

void DoExif(char *pDir)
{
    WIN32_FIND_DATA data;
    WIN32_FIND_DATA *datas[1000];

    HANDLE hFind = FindFirstFile("*.*", &data);
    char szThis[_MAX_PATH] = "";
    char szCurr[_MAX_PATH];
    BOOL bNext = FALSE;
    int nDirs = 0;

    if (pDir)
    {
        DoExifFolder(pDir, false);
        return;
    }

    GetCurrentDirectory(_MAX_PATH, szCurr);
    do
    {
        if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) != 0
            && stricmp(data.cFileName, ".") != 0
            && stricmp(data.cFileName, "..") != 0)
        {
            SetCurrentDirectory(data.cFileName);
            WIN32_FIND_DATA data2;
            HANDLE hFind2 = FindFirstFile("*.jpg", &data2);
            SetCurrentDirectory(szCurr);
            if (hFind2 != INVALID_HANDLE_VALUE)
            {
                FindClose(hFind2);

                datas[nDirs] = new WIN32_FIND_DATA;
                if (datas[nDirs])
                    memcpy(datas[nDirs], &data, sizeof(data));
                nDirs++;
            }

            do
            {
                bNext = FindNextFile(hFind, &data);
            } while (bNext &&
                ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) == 0
                    || stricmp(data.cFileName, ".") == 0
                    || stricmp(data.cFileName, "..") == 0));

        }
        else
            bNext = FindNextFile(hFind, &data);

    } while (bNext);

    qsort(datas, nDirs, sizeof(void *), SortData);


    FindClose(hFind);

    for (int i = 0; i < nDirs; i++)
    {
        SetCurrentDirectory(szCurr);
        strcpy(szThis, datas[i]->cFileName);
        strcpy(szFolder, datas[i]->cFileName);

        DoExifFolder(szFolder, false);

        if (nFiles > 0)
        {
            DeleteFileNames();
        }

    }
    SetCurrentDirectory(szCurr);

}

void DoGapsFolder(char *pFolder)
{
    char szRoot[256];
    _splitpath(szFolder, 0, 0, szRoot, 0);

    printf("Checking for gaps in %s\n", pFolder);

    if (!SetCurrentDirectory(szFolder))
    {
        printf("Unable to change to folder %s\n", szFolder);
        return;
    }
    GetCurrentDirectory(255, szFolder);

    nFiles = ScanFiles("*.jpg", szFolder, FALSE);
    if (nFiles == 0)
        return;
    qsort(szFileNames, nFiles, sizeof(char *), compare);

    for (int i = 0; i < nFiles - 1; i++)
    {
        int nFile1 = GetFileTitle(szFileNames[i]);
        int nFile2 = GetFileTitle(szFileNames[i + 1]);

        if (nFile1 >= 0 && nFile2 >= 0 && nFile2 - nFile1 > 1)
            printf("Gap between %s and %s\n", szFileNames[i], szFileNames[i + 1]);
    }
    return;

}

void DoGaps()
{
    WIN32_FIND_DATA data;
    WIN32_FIND_DATA *datas[1000];

    HANDLE hFind = FindFirstFile("*.*", &data);
    char szCurr[_MAX_PATH];
    BOOL bNext = FALSE;
    int nDirs = 0;

    GetCurrentDirectory(_MAX_PATH, szCurr);

    char *pRoot = strrchr(szCurr, '\\') + 1;

    do
    {
        if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) != 0
            && stricmp(data.cFileName, ".") != 0
            && stricmp(data.cFileName, "..") != 0)
        {
            SetCurrentDirectory(data.cFileName);
            WIN32_FIND_DATA data2;
            HANDLE hFind2 = FindFirstFile("*.jpg", &data2);
            SetCurrentDirectory(szCurr);
            if (hFind2 != INVALID_HANDLE_VALUE)
            {
                FindClose(hFind2);

                datas[nDirs] = new WIN32_FIND_DATA;
                if (datas[nDirs])
                    memcpy(datas[nDirs], &data, sizeof(data));
                nDirs++;
            }

            do
            {
                bNext = FindNextFile(hFind, &data);
            } while (bNext &&
                ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) == 0
                    || stricmp(data.cFileName, ".") == 0
                    || stricmp(data.cFileName, "..") == 0));

        }
        else
            bNext = FindNextFile(hFind, &data);

    } while (bNext);

    qsort(datas, nDirs, sizeof(void *), SortData);


    FindClose(hFind);

    for (int i = 0; i < nDirs; i++)
    {
        SetCurrentDirectory(szCurr);
        strcpy(szFolder, datas[i]->cFileName);

        DoGapsFolder(szFolder);

        if (nFiles > 0)
        {
            DeleteFileNames();
        }
    }

    SetCurrentDirectory(szCurr);
}

void DoList();

void RemoveHTML(char *pTitle)
{
    char *p = pTitle;
    while (*p)
    {
        if (*p == '<')
        {
            char *p1 = p;
            while (*p1 && *p1 != '>')
            {
                p1++;
            }
            if (*p1)
                memcpy(p, p1 + 1, strlen(p1));
            else
                *p = 0;
        }
        else
            p++;
    }
}
void DoListFolder(char *pFolder)
{
    char szRoot[256];
    char szLongName[256];
    _splitpath(szFolder, 0, 0, szRoot, 0);

    if (!SetCurrentDirectory(szFolder))
    {
        printf("Unable to change to folder %s\n", szFolder);
        return;
    }
    DoList();
    GetCurrentDirectory(255, szFolder);

    nFiles = ScanFiles("*.jpg", szFolder, FALSE);
    ReadTitles(".\\", szRoot, "titles.txt");


    if (nFiles == 0)
        return;
    qsort(szFileNames, nFiles, sizeof(char *), compare);

    for (int i = 0; i < nFiles; i++)
    {
        WIN32_FIND_DATA data;
        unsigned int nScale = 1; ;
        JpegFile jFile;
        unsigned int nWidth = 0, nHeight = 0;
        SYSTEMTIME sysTime;
        jFile.GetJPGDimensions(szFileNames[i], &nWidth, &nHeight);
        HANDLE hFind = FindFirstFile(szFileNames[i], &data);
        if (hFind)
        {
            char *pTitle;
            char szName[256];
            FileTimeToSystemTime(&data.ftLastWriteTime, &sysTime);
            FindClose(hFind);

            int nFile = GetFileTitle(szFileNames[i], szLongName);

            pTitle = GetTitle(szLongName);
            strcpy(szName, szFileNames[i]);
            if (strchr(szName, '-') == NULL)
            {
                char *pDot = strrchr(szName, '.');
                if (pDot)
                {
                    strcpy(pDot, "-0.jpg");
                }
            }
            RemoveHTML(pTitle);
            printf("\"%s\\%s\",\"%d\",\"%d\",\"%02d/%02d/%04d\",\"%s\"\n", szFolder, szName, nWidth, nHeight, sysTime.wDay, sysTime.wMonth, sysTime.wYear, pTitle);
        }

    }
    return;

}

void DoList()
{
    WIN32_FIND_DATA data;
    WIN32_FIND_DATA *datas[1000];

    HANDLE hFind = FindFirstFile("*.*", &data);
    char szCurr[_MAX_PATH];
    BOOL bNext = FALSE;
    int nDirs = 0;

    GetCurrentDirectory(_MAX_PATH, szCurr);

    char *pRoot = strrchr(szCurr, '\\') + 1;

    do
    {
        if ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) != 0
            && stricmp(data.cFileName, ".") != 0
            && stricmp(data.cFileName, "..") != 0)
        {
            SetCurrentDirectory(data.cFileName);
            WIN32_FIND_DATA data2;
            HANDLE hFind2 = FindFirstFile("*.jpg", &data2);
            SetCurrentDirectory(szCurr);
            if (hFind2 != INVALID_HANDLE_VALUE)
            {
                FindClose(hFind2);

                datas[nDirs] = new WIN32_FIND_DATA;
                if (datas[nDirs])
                    memcpy(datas[nDirs], &data, sizeof(data));
                nDirs++;
            }

            do
            {
                bNext = FindNextFile(hFind, &data);
            } while (bNext &&
                ((data.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) == 0
                    || stricmp(data.cFileName, ".") == 0
                    || stricmp(data.cFileName, "..") == 0));

        }
        else
            bNext = FindNextFile(hFind, &data);

    } while (bNext);

    qsort(datas, nDirs, sizeof(void *), SortData);


    FindClose(hFind);

    for (int i = 0; i < nDirs; i++)
    {
        SetCurrentDirectory(szCurr);
        strcpy(szFolder, datas[i]->cFileName);

        DoListFolder(szFolder);

        if (nFiles > 0)
        {
            DeleteFileNames();
        }
    }

    SetCurrentDirectory(szCurr);
}


void main(int argc, char **argv)
{
    int nStartTime = GetTickCount();
    char szCmd[256];
    static char szCurr[256];
    char *pUser;
    const char *buildString = "This build was compiled on " __DATE__ ", " __TIME__ ".";

    printf("%s\n", buildString);
    sprintf(szCmd, "dir \"%s\"", argv[0]);

    //	system ( szCmd ) ;
    if (__argc < 2)
    {
        printf("photos folder\n<-d description>\n<-r reverse>\n<-n next>\n<-p previous>\n<-t titles>\n<-s short_titles>\n");
        printf("e.g.\nphotos \"c:\\My Photos\" -d\"Holiday in Europe 1986\" -r -p\"../x/x.htm\" -n\"../y/y.htm\"");
        return;
    }


    strcpy(szFolder, __argv[1]);
    if (strcmp(szFolder, "*") == 0)
    {
        bAuto = TRUE;
    }
    if (strcmp(szFolder, "**") == 0)
    {
        bGaps = TRUE;
    }
    if (strcmp(szFolder, "***") == 0)
    {
        bExif = TRUE;
    }
    if (stricmp(szFolder, "*o") == 0)
    {
        bOrientation = TRUE;
    }

    if (strcmp(szFolder, "*List") == 0)
    {
        bList = TRUE;
    }

    GetCurrentDirectory(_MAX_PATH, szCurr);
    pRootFolder = strstr(szCurr, "\\My Photographs\\");


    strcpy(szThisRoll, "This roll");
    strcpy(szNextRoll, "Next roll");
    strcpy(szPrevRoll, "Previous roll");


    for (int i = 2; i < __argc; i++)
    {
        ParseCommandLine(__argv[i], i);
    }
    if (!bLes && (pUser = getenv("USERPROFILE")) != NULL)
    {
        sprintf(szDriveTitles1, "%s\\My Documents\\Google Drive\\titles", pUser);
        sprintf(szDriveTitles2, "%s\\Google Drive\\titles", pUser);
    }

    if (bLes)
    {
        bThumb = TRUE;
        strcpy(szThisRoll, "This page");
        strcpy(szNextRoll, "Next page");
        strcpy(szPrevRoll, "Previous page");
    }

    if (pRootFolder == NULL && !bLes && !bOrientation && !bRenameSort)
    {
        printf("Root folder %s must contain \"\\My Photographs\\\"\n", szFolder);
        return;
    }
    if (pRootFolder)
        pRootFolder += strlen("\\My Photographs\\");
    else
        pRootFolder = szCurr + strlen(szCurr);


    if (bMinutes)
    {
        strcpy(szThisRoll, "This book");
        strcpy(szNextRoll, "Next book");
        strcpy(szPrevRoll, "Previous book");
    }
    if (bStartIndex)
    {
        DoStartIndex();
        return;
    }
    if (bEndIndex)
    {
        DoEndIndex();
        return;
    }
    if (bDoFavourites)
    {
        char szCurr[256];
        CreateDirectory(szFolder, NULL);
        if (SetCurrentDirectory(szFolder))
        {
            DoFavourites(szFolder);
            SetCurrentDirectory(szCurr);
        }
        else
            printf("Can't set folder %s\n", szFolder);
        return;
    }
    if (bRenameSort)
    {
        if (!SetCurrentDirectory(szFolder))
        {
            printf("Unable to change to folder %s\n", szFolder);
            return;
        }

        nFiles = ScanFiles("*.jpg", szFolder, FALSE);
        RenameSort(szFileNames, rsName ? rsName : szFolder);
        return;
    }

    if (bAuto)
    {
        DoAuto();
        return;
    }
    if (bGaps)
    {
        DoGaps();
        return;
    }
    if (bList)
    {
        DoList();
        return;
    }
    if (bExif)
    {
        DoExif(argc >= 2 ? argv[2] : NULL);
        return;
    }
    if (bOrientation)
    {
        DoExifFolder(argc >= 2 ? argv[2] : NULL, true);
        return;
    }

    WIN32_FIND_DATA data;
    HANDLE hFind = FindFirstFile(szFolder, &data);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        FindClose(hFind);
        if ((data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) == 0) // It's a file!
        {
            if (!bPixellate)
                DoHtmlFile(szFolder);
            else
                Pixellate(szFolder, szPixelFile, nBig, nSmall, bCopy);
        }
        else
        {
            if (bCrunch)
                CrunchFiles(szFolder, szCrunchFile, nCCols, nCRows);
            else if (bScanTooSmall)
                ScanTooSmall(szFolder, nSmall);
            else
                DoHtmlFolder(szFolder);
        }
    }
    printf("%s completed successfully in %d ms\n", szFolder, GetTickCount() - nStartTime);

}
