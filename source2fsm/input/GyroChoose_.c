#if !defined(__IP_H__)
#define __IP_H__

//#include "std_basal.h"
//#include "std.h"

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint32_t unint32;
typedef uint16_t unint16;
typedef uint8_t unint08;
typedef float float32;

typedef void            (*Fun)(void *);

#define IPCALL(IP)		(IP.fun(&IP))


#define TRUE            			0xEB
#define FALSE           			0x00

#define FLT32_ZERO                 1.0E-6
// 绝对值函数
int ABS(int a) {
    return (a > 0) ? a : -a;
}

// 最小值函数
int MIN(int a, int b) {
    return (a > b) ? b : a;
}

#define SAM_DAMP            		0x00	/* SAM速率阻尼方式 */
#define SAM_PITCH           		0x11	/* SAM俯仰搜索方式 */
#define SAM_ROLL            		0x22	/* SAM滚动搜索方式 */
#define SAM_CRUISE          		0x33	/* SAM巡航方式 */
#define NOCTRL						0x44	/* 不控 */

#endif // __IP_H__

#if !defined(__GYROCHOOSE_H__)
#define __GYROCHOOSE_H__



void GyroChooseFun(void *p);

/* 选择参加定姿的陀螺 */
typedef struct __GyroChoose
{
    /* 接口函数 */
    Fun         fun;
    /* 输入端口 */
    unint08     StateFlag[9];                 /* 陀螺可用标志数组指针 */

    /* 输出端口 */
    unint08		JoinTotal;           	/* 参加定姿的陀螺个数 */
    unint16 	gyroStatus0;		 	/* 陀螺状态旧 */
    unint08		SignFlag[9] ; 		 	/* 参加定姿的陀螺序号 */
    /* 输入输出端口 */
    /* 状态变量 */
    /* 参数变量 */
} GyroChoose;

#endif // __GYROCHOOSE_H__


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