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

#if !defined(__MODESWITCH_H__)
#define __MODESWITCH_H__



void ModeSwitchFun(void *p);

/* 模式切换 */
typedef struct __ModeSwitch
{
    /* 接口函数 */
    Fun         fun;
    /* 输入端口 */
    float32     *pGyroRate;                 /* 陀螺角速度数组指针 */
	unint32 	flgSP;                      /* 见太阳标志 */     
	float32 	royaw;                      /* 太阳滚动 */  
	float32 	piyaw;                      /* 太阳俯仰 */  
    /* 输出端口 */
    unint32     m_workMode;                     /* 工作模式 */
    /* 输入输出端口 */
    /* 状态变量 */
    unint32     m_countMode;                        
    unint32     m_countPublic;                        
    /* 参数变量 */
    unint32     time_D2P;                       /* 速率阻尼连续稳定转俯仰搜索时间（控制周期） */
    unint32     time_D2P_overtime;              /* 速率阻尼不能稳定转俯仰搜索时间（控制周期） */
} ModeSwitch;

#endif // __MODESWITCH_H__



void SAMSubModeDamp(ModeSwitch* this);
void SAMSubModePitch(ModeSwitch* this);
void SAMSubModeRoll(ModeSwitch* this);
void SAMSubModeCruise(ModeSwitch* this);

void ModeSwitchFun(void *p)
{
    ModeSwitch *pIp = (ModeSwitch*)p;
    
    /* 进行模式切换流程 */
    switch ( pIp->m_workMode )
    {
    case SAM_DAMP:
        SAMSubModeDamp(pIp);
        break;
    case SAM_PITCH:
        SAMSubModePitch(pIp);
        break;
    case SAM_ROLL:
        SAMSubModeRoll(pIp);
        break;
    case SAM_CRUISE:
        break;
    default:
        break;
    }
    return;
}

void SAMSubModeDamp(ModeSwitch *this)
{
    float32 fabsmax;										/* 临时：绝对值最大 */

    fabsmax = TripleFabsMax( this->pGyroRate[0], this->pGyroRate[1], this->pGyroRate[2] ) ;/* 求三轴姿态角速度最大值 */

    if ( fabsmax < 0.15f )		 							/* 三轴姿态角速度均小于0.15度/秒 */
    {
        this->m_countPublic++ ;								/* 方式计数器 */
    }

    /* 若700Ts角速度都小于0.07度/s 或 速率阻尼持续时间大于128秒时,置俯仰角速度偏置为-0.5度/s, 转入俯仰搜索 */
    if (( this->m_countPublic > this->time_D2P ) || ( this->m_countMode > this->time_D2P_overtime )) 									
    {       
        this->m_workMode = SAM_PITCH;
                                                                                         
        this->m_countMode = 0 ;									/* 清控制周期计数器 */
        this->m_countPublic = 0 ;								/* 方式计数器 */
    }       
    return;
}
void SAMSubModePitch(ModeSwitch *this)
{
    float32 pirawtmp;
    if (this->flgSP == TRUE)						   		    /* 若SP标志为见太阳 */
    {
       pirawtmp = ABS(this->piyaw);

       if (pirawtmp > 0.25f)								/* 太敏俯仰测量角 > 0.25度 */
       {
           this->m_countPublic++;							/* 方式计数器 */

           if (this->m_countPublic > 12)    				/* 持续12TS,则太阳搜索完成,转巡航 */
           {
               /* 转入SAM巡航方式 */
               this->m_workMode = SAM_CRUISE;			/* 置巡航方式字 */
               this->m_countMode = 0;						/* 清控制周期计数 */
               this->m_countPublic = 0;					/* 方式计数器 */
           }
       }
    }
    else
    {
       this->m_countPublic = 0;							/* 方式计数器 */
    }

    if (this->m_countMode > 4500)							/* 若720秒太阳仍不出现,置ωx=0.5度/秒,ωy=0度/秒,转滚动搜索 */
    {
       this->m_workMode = SAM_ROLL;					    /* 转入SAM滚动搜索方式 */
       this->m_countMode = 0;								/* 控制周期计数器 */
       this->m_countPublic = 0;							/* 方式计数器 */
    }
    return;
}
void SAMSubModeRoll(ModeSwitch *this)
{
    float32 tmproyaw ;								
    
    if (this->flgSP == TRUE)										/* 若SP=1 */
    {
    	tmproyaw = ABS(this->royaw) ;
    	
    	if ( tmproyaw > 1.0f )								/* 限幅 */
    	{                                                   
        	this->m_countPublic++ ;							/* 方式计数器计数 */
        	                                                
        	if (this->m_countPublic > 12)					/* 方式计数器13=2.08s 〉2.048s */
        	{                                               
                this->m_workMode = SAM_CRUISE;
        		this->m_countMode = 0 ;						/* 控制周期计数器 */							
        		this->m_countPublic = 0 ;					/* 方式计数器清零 */			
        	}
    	}
    }
    else
    {
        this->m_countPublic = 0 ;							 /* 方式计数器清零 */		
    }                                                       
                                                            
                                                            
    if (this->m_countMode > 5000)								     /* 若800s太阳仍不出现,置ωx=0度/秒,ωy=-0.5度/秒,重新俯仰搜索 */
    {
        this->m_workMode = SAM_PITCH;
        this->m_countMode = 0;								 /* 控制周期计数器 */							
        this->m_countPublic = 0;							 /* 方式计数器清零 */		    	
    }
    return;
}
void SAMSubModeCruise(ModeSwitch *this)
{

    return;
}