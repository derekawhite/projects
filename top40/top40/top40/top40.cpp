// top40.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "string.h"

static char g_year[5] = "";
void strip(char *line)
{
    int len = strlen(line);

    while (len > 0 && (line[0] == '\r' || line[0] == '\n' || line[0] == '\t' || line[0] == ' '))
    {
        memcpy(line, &line[1], len);
        len--;
    }

    while (len > 0 && (line[len - 1] == '\r' || line[len - 1] == '\n' || line[len - 1] == '\t' || line[len - 1] == ' '))
        line[--len] = '\0';
}

void getdmy(char *line, char *day, char*month, char *year)
{
    int n = 0;

    for (n = 0; *line != '\0' && *line != ' ' && n++ < 2; day++, line++)
        *day = *line;
    *day = 0;
    for (n = 0, ++line; *line != '\0' && *line != ' '&& n++ < 9;month++, *line++)
        *month = *line;
    *month = 0;
    for (n = 0, ++line; *line != '\0' && *line != ' '&& n++ < 4;year++, *line++)
        *year = *line;
    *year = 0;

}

int getpos(char *line)
{
    int nOld, nNew;
    char szNew[100];
    char x[100],y[100],z[100];

    int res = sscanf_s(line, "%s %s %s", x, 100, y, 100, z, 100);
    if (res == 2)
    {
        if (sscanf_s(line, "%d %d", &nNew, &nOld) == 2)
        {
            return nNew;
        }
        if (sscanf_s(line, "%d %s", &nNew, szNew, 100) == 2 && _stricmp(szNew, "new") == 0)
        {
            return nNew;
        }
    }
    return -1;
}
void striplastwords(char *line, int nwords)
{
    int len = strlen(line);
    for (; len > 0 && nwords > 0;nwords--)
    {
        while (len > 0 && line[len - 1] == ' ')
            line[--len] = '\0';
        while ( len > 0 && line[len - 1] != ' ')
            line[--len] = '\0';
    }
    while (len > 0 && line[len - 1] == ' ')
        line[--len] = '\0';
}

void escape(char *line)
{
    int len = strlen(line);
    int i = 0;
    for (i = 0; i < len; i++)
    {
        if (line[i] == '\'' || line[i]=='&')
        {
            int j = 0;
            for (j = len + 1; j > i; j--)
                line[j] = line[j - 1];
            len++;
            if (line[i] == '&')
                line[i] = '\\';
            i++;
        }
    }
}

void ProcessLine(char *line, FILE *in, FILE* out, char *pdate=NULL)
{
    char date[20]="";
    static bool bFirst = true;

    strip(line);
    if (strstr(line, "Official Singles Chart Top") != 0)
    {
        char day[3] = "", month[10] = "", year[5] = "";
        char newl[1000];
        fgets(newl, 999, in);
        strip(newl);
        getdmy(newl, day, month, year);
        if (g_year[0] == '\0' && year[0] != '\0')
            strcpy_s(g_year,5, year);
        sprintf_s(date, "%02s %s %s", day, month, year);
        if (bFirst)
        {
            bFirst = false;
            fprintf(out, "drop table charts%s;\ncreate table charts%s ( week date, position number, title varchar2(100), artist varchar2(100));\nset escape on;\n", year, year);
        }
        while  (fgets(newl, 999, in))
        {
            strip(newl);
            ProcessLine(newl, in, out, date);
        } 
    }
    else if (pdate)
    {
        int pos = getpos(line);
        if (pos >= 1 && pos <= 40)
        {
            char artist[1000], song[1000];
            if (fgets(song, 999, in) && fgets(song, 999, in) && fgets(artist, 999, in))
            {
                strip(song);
                strip(artist);
                striplastwords(artist, 3);
                escape(artist);
                escape(song);
                fprintf(out, "insert into charts%s values (to_date('%s', 'dd month yyyy'),'%d','%s','%s');\n",g_year, pdate, pos, song, artist);
            }

        }
    }
}
int _tmain(int argc, _TCHAR* argv[])
{
    char pin[256];
    char pout[256];

    FILE *in, *out;
    char line[1000];

    if (argc <= 1)
    {
        printf("usage: top40 year");
        return 1;
    }

    sprintf_s(pin, "C:\\Users\\derek.white\\Google Drive\\Documents\\Charts\\%S\\top40-%S.txt", argv[1], argv[1]);
    sprintf_s(pout, "C:\\Users\\derek.white\\Google Drive\\Documents\\Charts\\%S\\top40-%S.sql", argv[1], argv[1]);

    if (fopen_s(&in, pin, "r") == 0)
    {
        if (fopen_s(&out, pout, "w") == 0)
        {
            while (fgets(line, 999, in))
            {
                strip(line);
                ProcessLine(line, in, out);
            }
            fprintf(out, "select min(position) pos,title,artist from charts%s group by title, artist order by pos desc;\n", g_year);
            fclose(out);
        }
        fclose(in);
    }

    return 0;
}

