#include "GyroChoose.h"
#include <time.h>
#include <stdio.h>

void GyroChooseFun(void *p)
{
    GyroChoose *pIp = (GyroChoose*)p;
	unint08 i ;									      		/* 循环用临时变量 */
	/* 确定参加工作陀螺的个数 */                             
	pIp->JoinTotal = 0 ;								/* 参加定姿的陀螺个数清零 */
	pIp->gyroStatus0 = 0 ;								 
	                                                         
	for ( i=0 ; i<9 ; i++ )									/* 9个陀螺进行判断 */
	{	                                                     
		if (pIp->StateFlag[i] == TRUE)  				/* 如果陀螺状态正常 */
		{	                                                 
			pIp->SignFlag[pIp->JoinTotal] = i ;	/* 统计参加定姿的陀螺螺序号 */
			pIp->JoinTotal++ ;							/* 统计参加定姿的陀螺个数 */	
			pIp->gyroStatus0 = pIp->gyroStatus0 | (1 << i) ;									
		}
	}
    return;
}

int randi(int min,int max){
	return rand()%(max-min)+min;
}

void randis(int min,int max,int n,unint08* re){
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

GyroChoose GyroChoose1 = {.fun = GyroChooseFun};

void main(){
	srand(time(0));
	for (int i = 0; i < 20; i++)
	{              
		randis(0,255,9,GyroChoose1.StateFlag);
		for (int j=0 ; j<9 ; j++ )	{
			if (randi(0,10)>6) {
			GyroChoose1.StateFlag[i] = TRUE;
		}
		}
        IPCALL(GyroChoose1);		
	}
}