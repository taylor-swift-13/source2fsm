#include<stdio.h>
#include<stdlib.h>

int main(){
 
 printf("hello");

 int a = 10;
 int b = 5;
 int c = 3;

 scanf("%d", &c);
 
 int * p=(int*)malloc(sizeof(int));

 if(a>b&&b>c){
   a++;
 }
 
 if(a>b){
   if(a>b){
      a++;
   }
   a++;
   a++;
   a++;
 }

 if(a>b){
   a++;
   a++;
   a++;
   a++;
   a++;
   b++;
   a++;
 }

 switch (a)
    {
    case 10:
        a++;
        break;
    case 11:
        a++;
        break;
    case 12:
        a++;
        break;
    case 13:
        a++;
        break;
    default:
        break;
    }

 return 0;

}