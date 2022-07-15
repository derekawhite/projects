// killcontroller.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <windows.h>
#include <psapi.h>
#include <winbase.h>
#include "string"

void KillModule( DWORD processID, const char* exename, BOOL bKill )
{
    HMODULE hMods[2048];
    HANDLE hProcess;
    DWORD cbNeeded;
    unsigned int i;
    BOOL bRet ;

    // Get a list of all the modules in this process.

    hProcess = OpenProcess(PROCESS_ALL_ACCESS,
        TRUE, processID );
    if (NULL == hProcess)
        return ;

    if( (bRet = EnumProcessModules(hProcess, hMods, sizeof(hMods), &cbNeeded)) == TRUE)
    {
        for ( i = 0; i < (cbNeeded / sizeof(HMODULE)); i++ )
        {
            char szModName[MAX_PATH];

            // Get the full path to the module's file.
            if (GetModuleFileNameExA(hProcess, hMods[i], szModName,
                sizeof(szModName)))
            {
                char szCmpName[_MAX_PATH];
                char szExeName[_MAX_PATH];
                strcpy_s(szCmpName, _MAX_PATH, szModName);
                _strupr_s(szCmpName, MAX_PATH);

                strcpy_s(szExeName, _MAX_PATH, exename);
                _strupr_s(szExeName, MAX_PATH);

                if (strstr(szCmpName, szExeName))
                {
                    if (bKill)
                    {
                        printf("Killing %s (PID %d)\n", szModName, processID);
                        TerminateProcess(hProcess, 0);
                        break;
                    }
                    else
                    {
                        printf("Found %s (PID %d)\n", szModName, processID);
                        break;
                    }
                }
            }
        }
    }
    else
    {
       // printf("Error killing PID %d\n", processID);
    }

    CloseHandle( hProcess );
}

void kill_processes (const char* exename, BOOL bKill)
{
    DWORD aProcesses[1024], cbNeeded, cProcesses;
    unsigned int i;

    // Enable SeDebugPrivilege
    HANDLE hToken = NULL;
    TOKEN_PRIVILEGES tokenPriv;
    LUID luidDebug;
    if (OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &hToken) != FALSE)
    {
        if (LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &luidDebug) != FALSE)
        {
            tokenPriv.PrivilegeCount = 1;
            tokenPriv.Privileges[0].Luid = luidDebug;
            tokenPriv.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
            if (AdjustTokenPrivileges(hToken, FALSE, &tokenPriv, 0, NULL, NULL) != FALSE)
            {
                // Always successful, even in the cases which lead to OpenProcess failure
                printf("SUCCESSFULLY CHANGED TOKEN PRIVILEGES\n");
            }
            else
            {
                printf("FAILED TO CHANGE TOKEN PRIVILEGES, CODE: %d\n", GetLastError());
            }
        }
    }
    CloseHandle(hToken);
    // Enable SeDebugPrivilege

    // trawl through all of the running processes and see which one has a module name matching exename   
    if (!exename || !strlen(exename))
        return ;

    if ( !EnumProcesses( aProcesses, sizeof(aProcesses), &cbNeeded ) )
        return ;

    // Calculate how many process identifiers were returned.
    cProcesses = cbNeeded / sizeof(DWORD);

    printf("cProcesses = %d\n", cProcesses);
    
    // Look for the corresponding module name
    for ( i = 0; i < cProcesses; i++ )
    {
        KillModule( aProcesses[i], exename, bKill);
    }

}


void stop_service ( char *svc_name )
{
	SC_HANDLE schSCManager = OpenSCManager(
        NULL,                   // machine (NULL == local)
        NULL,                   // database (NULL == default)
        SC_MANAGER_ALL_ACCESS   // access required
	) ;
    if ( schSCManager )
    {
		SC_HANDLE schService = OpenServiceA(schSCManager, svc_name, SERVICE_ALL_ACCESS);

        if (schService)
        {
            // try to stop the service
            SERVICE_STATUS        service_status;
            if ( ControlService( schService, SERVICE_CONTROL_STOP, &service_status ) )
            {
              	printf ( "Stopping %s\n", svc_name) ;
			}
            CloseServiceHandle(schService);
        }
        CloseServiceHandle(schSCManager);
	}
}

inline std::string convert(const std::wstring& as)
{
    char* buf = new char[as.size() * 2 + 2];
    sprintf_s(buf, as.size() * 2 + 2, "%S", as.c_str());
    std::string rval = buf;
    delete[] buf;
    return rval;
}

int _tmain(int argc, _TCHAR* argv[])
{
    //stop_service ("BankWorld Controller") ;

    const char *buildString = "This build was compiled on " __DATE__ ", " __TIME__ ".";
    printf("%s\n", buildString);

    if (argc < 2)
    {
        kill_processes("BUILD\\BWOUT", TRUE);
        kill_processes("JAVA.EXE", TRUE);
    }
    else if (wcscmp(argv[1], _T("list")) == 0)
    {
        kill_processes("BUILD\\BWOUT", FALSE);
        kill_processes("JAVA.EXE", FALSE);
    }
    else if ((argc > 2) && wcscmp(argv[1], _T("-k")) == 0)
    {
        std::wstring wst = argv[2];
        std::string nst = convert(wst);
        const char *pst = nst.c_str();
        kill_processes(pst, TRUE);
    }


}

