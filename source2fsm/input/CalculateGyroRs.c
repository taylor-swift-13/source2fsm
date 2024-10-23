#include "CalculateGyroRs.h"

void CalculateGyroRsFun(void *p)
{
    CalculateGyroRs *pIp = (CalculateGyroRs*)p;
	unint08 i ;									
 	unint08 j ;									
	unint08 k ;									
 	float32 Rgtrans[3][5] ;									
 	float32 Rs[3][3] ;									
	float32 RsInv[3][3] ;									
 	float32 Rgtemp[5][3] ;									

 	pIp->JoinTotal = MIN(pIp->JoinTotal, 5) ;												
  	                                                                        	
	if (pIp->gyroStatus0 != pIp->gyroStatus1)		/* 有陀螺切换 */
	{		                                                
		pIp->flgGryoCalc = TRUE ;								/* 置陀螺计算标志 */
			                                                
		for ( j=0 ; j<pIp->JoinTotal ; j++ )			/* 参加定姿的陀螺个数 */
		{                                                               				
			k = pIp->SignFlag[j] ;						/* 按从小到大排列依次选5个，不足5个选余下的 */								
		                                                                				
			for ( i=0 ;  i<3 ; i++ )                        
			{                                               
				Rgtemp[j][i] = pIp->VG[k][i] ;					/* n*3的安装阵R */						
			}                                               
		}                                                   
                                                            
		for ( i = pIp->JoinTotal ; i<5 ; i++ )			/* 不用的（5-JoinTotal）维，清零 */
		{
			for ( j=0 ; j<3 ; j++ )
			{
				Rgtemp[i][j] = 0.0f;										
			}
		}

		if (pIp->JoinTotal >= 3)						/* 若大于三个陀螺工作可以计算角速度 */
		{                                                                       
			                                                                    
			MatrixTran(&Rgtrans[0][0], &Rgtemp[0][0], 5, 3) ;					/* Rg->Rgtrans    		*/								
			MatrixMulti(&Rs[0][0], &Rgtrans[0][0], &Rgtemp[0][0], 3, 5, 3) ;	/* R*RT->RS       		*/								
			MatrixInv33F(&RsInv[0][0], &Rs[0][0]) ;								/* INV(RS)->RsInv 		*/		
			MatrixMulti(&pIp->Rtemp[0][0], &RsInv[0][0], &Rgtrans[0][0], 3, 3, 5) ;	/* RsInv*Rgtrans->Rtemp */									
		}		
		pIp->gyroStatus1 = pIp->gyroStatus0 ;									
	}
    return;
}
