// Quick throughput test: raw 7x7 CA steps per second on an NVIDIA GPU (one grid per thread).
// Build: nvcc -O3 -arch=sm_86 gpu_bench_7x7.cu   (RTX 3060 laptop: ~2e10 steps/s)
#include <cstdio>
#include <cstdint>
typedef unsigned long long u64;
#define N 7
#define CELLS 49
__device__ __forceinline__ u64 vrot(u64 x,int s){int k=s*N;return ((x<<k)|(x>>(CELLS-k)))&((1ull<<CELLS)-1);}
__global__ void run(u64 seed,int rule,int iters,u64* out,u64 COL0,u64 COLLAST){
  u64 i=blockIdx.x*(u64)blockDim.x+threadIdx.x; u64 x=(seed^(i*0x9E3779B97F4A7C15ull))*0xBF58476D1CE4E5B9ull; x&=(1ull<<CELLS)-1;
  const u64 M=(1ull<<CELLS)-1; u64 acc=0;
  for(int t=0;t<iters;t++){
    u64 e=((x>>1)&~COLLAST)|((x<<(N-1))&COLLAST); u64 w=((x<<1)&~COL0&M)|((x>>(N-1))&COL0);
    u64 nb[8]={e,w,vrot(x,1),vrot(x,N-1),vrot(e,1),vrot(e,N-1),vrot(w,1),vrot(w,N-1)};
    u64 b0=0,b1=0,b2=0,b3=0;
    #pragma unroll
    for(int k=0;k<8;k++){u64 c0=b0&nb[k];b0^=nb[k];u64 c1=b1&c0;b1^=c0;u64 c2=b2&c1;b2^=c1;b3|=c2;}
    u64 o=0;
    #pragma unroll
    for(int k=0;k<=8;k++) if(rule>>k&1) o|=((k&1)?b0:~b0)&((k&2)?b1:~b1)&((k&4)?b2:~b2)&((k&8)?b3:~b3);
    x=o&M; acc+=x;
  }
  out[i]=acc;
}
int main(){
  u64 COL0=0,COLLAST=0; for(int r=0;r<N;r++){COL0|=1ull<<(r*N);COLLAST|=1ull<<(r*N+N-1);}
  int threads=1<<20, iters=2000; u64* d; cudaMalloc(&d,threads*8);
  run<<<threads/256,256>>>(1,172,10,d,COL0,COLLAST); cudaDeviceSynchronize();
  cudaEvent_t a,b; cudaEventCreate(&a);cudaEventCreate(&b); cudaEventRecord(a);
  run<<<threads/256,256>>>(2,172,iters,d,COL0,COLLAST); cudaEventRecord(b); cudaEventSynchronize(b);
  float ms; cudaEventElapsedTime(&ms,a,b); printf("%.3g steps/s\n",(double)threads*iters/(ms/1000));
}
