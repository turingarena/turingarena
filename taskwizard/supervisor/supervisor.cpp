#include <stdlib.h>
#include <stdio.h>

#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>

#include <string>
using namespace std;

void copy_totmp(const char *temp, const char *driver, const char *exec)
{
    int childExitStatus;
    pid_t pid;
    int status;
    pid = fork();

    if (pid == 0) { /* child */
        int r = execl("./make_tmp.sh", "make_tmp.sh", "", temp, driver, exec, (char *)0);
        if (r == -1)printf("r = %d   errno = %d\n",r,errno);
        exit(0);
    }
    else if (pid < 0) {
        /* error - couldn't start process - you decide how to handle */
    }
    else {

        /* parent - wait for child - this has all error handling, you
         * could just call wait() as long as you are only expecting to
         * have one child process at a time.
         */
        pid_t ws = waitpid( pid, &childExitStatus, 0);
        if (ws == -1)
        { /* error - handle as you wish */
        }

        if( WIFEXITED(childExitStatus)) /* exit code in childExitStatus */
        {
            status = WEXITSTATUS(childExitStatus); /* zero is normal exit */
            /* handle non-zero as you wish */
        }
        else if (WIFSIGNALED(childExitStatus)) /* killed */
        {
        }
        else if (WIFSTOPPED(childExitStatus)) /* stopped */
        {
        }
    }
}

void read_from_pipe (int file)
 {
   FILE *stream;
   int c;
   stream = fdopen (file, "r");
   while ((c = fgetc (stream)) != EOF)
     putchar (c);
   fclose (stream);
 }

void make_fd(int index) {
    char read_fd[50]; 
    char write_fd[50]; 

    sprintf(read_fd, "rfdesc%d", index);
    sprintf(write_fd, "wfdesc%d", index);

    mkfifo(read_fd, 0666);
    mkfifo(write_fd, 0666);

    printf("Created.\n");
}

FILE* open_fd_writetochild(int index) {
    char read_fd[50]; 
    sprintf(read_fd, "rfdesc%d", index);
    return fopen(read_fd, "w");
}

FILE* open_fd_readfromchild(int index) {
    char write_fd[50]; 
    sprintf(write_fd, "wfdesc%d", index);
    return fopen(write_fd, "r");
}


FILE* open_fd_childwrites(int index) {
    char write_fd[50]; 
    sprintf(write_fd, "wfdesc%d", index);
    return fopen(write_fd, "w");
}

FILE* open_fd_childreads(int index) {
    char read_fd[50]; 
    sprintf(read_fd, "rfdesc%d", index);
    return fopen(read_fd, "r");
}

static FILE *inpipes[2000];
static FILE *outpipes[2000];

void run_client(int index) { // index > 0!!!
    make_fd(index); // Make control file descriptors

    pid_t pid = fork();
    
    if (pid == 0) { /* child */
        
        dup2(fileno(open_fd_childwrites(index)), STDOUT_FILENO);
        dup2(fileno(open_fd_childreads(index)), STDIN_FILENO);


        int r = execl("./solution", "solution", (char *)0);
        if (r == -1) printf("r = %d   errno = %d\n",r,errno);
        exit(0);
    }

    inpipes[index] = open_fd_readfromchild(index);
    outpipes[index] = open_fd_writetochild(index);
    setvbuf(outpipes[index], NULL, _IONBF, 0);
}

FILE *ctrlout;
FILE *ctrlin;

void run_driver() {
    make_fd(0); // Make control file descriptors

    pid_t pid = fork();
    
    if (pid == 0) { /* child */
        
        dup2(fileno(open_fd_childwrites(0)), STDOUT_FILENO);
        dup2(fileno(open_fd_childreads(0)), STDIN_FILENO);


        int r = execl("./driver", "driver", (char *)0);
        if (r == -1) printf("r = %d   errno = %d\n",r,errno);
        exit(0);
    }

    ctrlin = open_fd_readfromchild(0);
    ctrlout = open_fd_writetochild(0);
    setvbuf(ctrlout, NULL, _IONBF, 0);
}




char tempdir[5000];
char* make_env(const char *taskfolder, const char *submission) {
    char temp[] = "/tmp/tmpdir.XXXXXX";
    char *tmp_dirname = mkdtemp (temp);
    strcpy(tempdir, tmp_dirname);
    tmp_dirname = tempdir;

    if (tmp_dirname == NULL) {
        exit(1);
    }

    char driver[300];
    sprintf(driver, "%s/%s", taskfolder, "driver");

    printf("Folder: %s\n", tmp_dirname);

    copy_totmp(tmp_dirname, driver, submission);
    chdir(tmp_dirname);
    return tmp_dirname;
}


int main(int argc, char** argv) {

    if (argc != 3) {
        printf("Only a task directory and an executable file should be specified\n");
        return 1;
    }
    make_env(argv[1], argv[2]);


    run_driver();
    run_client(1);

    
    char ex[500];

    //for (int i = 0; i < 2; i++) {
    fprintf(stderr, "Waiting...\n");
    fscanf(ctrlin, "%s", ex);
    fprintf(stderr, "String: %s\n", ex);
    fprintf(ctrlout, "1\n"); // write id

    fscanf(ctrlin, "%s", ex); // read response
    for (int i = 0; i < 10; i++)
    fprintf(stderr, "%s\n", ex);


    //}

    //fscanf(inpipes[1], "%s", ex);
    //printf ("Solution response: %s\n", ex);

}