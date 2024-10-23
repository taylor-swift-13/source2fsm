#include "PseudoRate.h"

void PseudoRateFun(void *p)
{
    PseudoRate *pIp = (PseudoRate*)p;
    unint32 i;
    for (i = 0; i < 3; i++)
    {
        if ((pIp->pu[i] - pIp->r[i]) > pIp->h1[i])					/* u(输入)-r（反馈信号）>h1 */		
        {                                                           
            pIp->Yp[i] = 0x0 ;									/* 产生32ms正脉冲 */
            pIp->Yn[i] = 0xF ;									
            pIp->r[i] = 0.9231f * pIp->r[i] + 0.07688f ;	/*  Y=1 */						
        }                                                           
        else if ((pIp->pu[i] - pIp->r[i]) < -pIp->h1[i])				/* u(输入)-r（反馈信号）<h1 */		
        {                                                           
            pIp->Yp[i] = 0xF ;									/* 产生32ms负脉冲 */
            pIp->Yn[i] = 0x0 ;									
            pIp->r[i] = 0.9231f * pIp->r[i] - 0.07688f ;	/* Y=-1  */						
        }                                                           
        else														/* 其他 */
        {                                                           
            pIp->Yp[i] = 0x0 ;									/* 不喷 */						
            pIp->Yn[i] = 0x0 ;									
            pIp->r[i] = 0.9231f * pIp->r[i] ;				/* Y=0  */						
        }      
    }
    return;
}

int randi(int min,int max){
	return rand()%(max-min)+min;
}

void randis(int min,int max,int n,int* re){
    for(int i=0; i<n; i++)
        re[i] = rand()%(max-min)+min;
}

float32 randf(float32 min,float32 max){
	return min+1.0*(rand()%RAND_MAX)/RAND_MAX *(max-min);
}

void randfs(float32 min,float32 max,int n,float32* re){
    for(int i=0; i<n; i++)
        re[i] = min+1.0*(rand()%RAND_MAX)/RAND_MAX *(max-min);
}

PseudoRate PseudoRate1 =
{
    .fun = PseudoRateFun,
};

int main(){
	srand(time(0));
	for (int i = 0; i < 20; i++)
	{       
		randfs(-126,127,3, PseudoRate1.h1);
        int n=randi(3,50);
        PseudoRate1.pu = (float32 *) malloc(sizeof(float32) * n);
		randfs(-126,127,n,PseudoRate1.pu);
        IPCALL(PseudoRate1);
        free(PseudoRate1.pu);		
	}
    return 0;
}