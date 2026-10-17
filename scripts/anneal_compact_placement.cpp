// Constructive development placer. Input/output is a compact numeric protocol;
// the Python wrapper independently checks every constraint before acceptance.
#include <algorithm>
#include <array>
#include <cmath>
#include <chrono>
#include <iostream>
#include <random>
#include <vector>
using namespace std;
struct Part {array<array<double,4>,4> box,body,cu; array<vector<array<double,2>>,4> pins; double xmin,xmax,ymin,ymax;int mask;};
struct Pose {double x,y;int r;};
struct Link {int a,pa,b,pb;double maxd;};
int main(){int n,k,clock_index,mcu_index;double seconds;unsigned seed;cin>>n>>k>>seconds>>seed>>clock_index>>mcu_index;vector<Part> p(n);vector<Pose> q(n),best;vector<vector<double>> gaps(n,vector<double>(n));vector<Link> links(k);vector<vector<int>> by(n);
for(int i=0;i<n;i++){auto &t=p[i];cin>>t.mask>>t.xmin>>t.xmax>>t.ymin>>t.ymax>>q[i].x>>q[i].y>>q[i].r;int np;cin>>np;for(int r=0;r<4;r++){for(double &v:t.box[r])cin>>v;for(double &v:t.body[r])cin>>v;for(double &v:t.cu[r])cin>>v;t.pins[r].resize(np);for(auto &v:t.pins[r])cin>>v[0]>>v[1];}}
for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)cin>>gaps[i][j];
for(int l=0;l<k;l++){auto &v=links[l];cin>>v.a>>v.pa>>v.b>>v.pb>>v.maxd;by[v.a].push_back(l);by[v.b].push_back(l);}
auto sq=[](double x){return x>0?x*x:0.;};
auto penetration=[](array<double,4>a,Pose x,array<double,4>b,Pose y,double gap){double dx=min(a[2]+x.x-b[0]-y.x,b[2]+y.x-a[0]-x.x)+gap;double dy=min(a[3]+x.y-b[1]-y.y,b[3]+y.y-a[1]-x.y)+gap;return dx>0&&dy>0?pow(min(dx,dy),2):0.;};
auto single=[&](int i){auto &v=q[i];auto &t=p[i];auto b=t.box[v.r];auto c=t.cu[v.r];return 30*(sq(-14.15-b[0]-v.x)+sq(b[2]+v.x-14.15)+sq(-14.15-b[1]-v.y)+sq(b[3]+v.y-14.15)+sq(-13.75-c[0]-v.x)+sq(c[2]+v.x-13.75)+sq(-13.75-c[1]-v.y)+sq(c[3]+v.y-13.75)+sq(t.xmin-v.x)+sq(v.x-t.xmax)+sq(t.ymin-v.y)+sq(v.y-t.ymax));};
auto paircost=[&](int i,int j){double cost=penetration(p[i].box[q[i].r],q[i],p[j].box[q[j].r],q[j],0);double g=gaps[min(i,j)][max(i,j)];if(g>0)cost=max(cost,penetration(p[i].body[q[i].r],q[i],p[j].body[q[j].r],q[j],g));if((i==clock_index&&j==mcu_index)||(j==clock_index&&i==mcu_index)){auto yc=p[clock_index].cu[q[clock_index].r];auto mc=p[mcu_index].cu[q[mcu_index].r];cost+=sq(yc[3]+q[clock_index].y+.55-mc[1]-q[mcu_index].y);}return 30*cost;};
auto wire=[&](int l){auto &v=links[l];auto a=p[v.a].pins[q[v.a].r][v.pa];auto b=p[v.b].pins[q[v.b].r][v.pb];double d=abs(a[0]+q[v.a].x-b[0]-q[v.b].x)+abs(a[1]+q[v.a].y-b[1]-q[v.b].y);return 15*sq(d-v.maxd)+.001*d;};
auto local=[&](int i){double c=single(i);for(int j=0;j<n;j++)if(i!=j)c+=paircost(i,j);for(int l:by[i])c+=wire(l);return c;};
auto total=[&](){double c=0;for(int i=0;i<n;i++){c+=single(i);for(int j=i+1;j<n;j++)c+=paircost(i,j);}for(int l=0;l<k;l++)c+=wire(l);return c;};
mt19937 rng(seed);uniform_real_distribution<double> u(0,1);auto roundgrid=[](double x){return round(x*20)/20;};double current=total(),lowest=current;best=q;auto start=chrono::steady_clock::now();long iterations=0;double elapsed=0;
while((elapsed=chrono::duration<double>(chrono::steady_clock::now()-start).count())<seconds){int i=rng()%n;Pose old=q[i];double oldcost=local(i);double cycle=fmod(elapsed,20)/20;double temp=8*pow(.002,cycle);double rad=cycle<.4?2:cycle<.8?.5:.15;
if(u(rng)<.03){q[i].x=roundgrid(-13+26*u(rng));q[i].y=roundgrid(-13+26*u(rng));}else{q[i].x+=roundgrid((u(rng)-.5)*2*rad);q[i].y+=roundgrid((u(rng)-.5)*2*rad);}
if(u(rng)<.10){int r=rng()%4;if(p[i].mask&(1<<r))q[i].r=r;}
double diff=local(i)-oldcost;if(diff<=0||u(rng)<exp(-diff/temp))current+=diff;else q[i]=old;
if(current<lowest){lowest=current;best=q;}
if(++iterations%20000000==0){cerr<<"Iterations "<<iterations<<" cost "<<lowest<<" elapsed "<<elapsed<<"\n";}
if(cycle>.995&&u(rng)<.05){q=best;current=total();}
}
q=best;lowest=total();cout<<lowest<<" "<<iterations<<"\n";for(auto v:best)cout<<v.x<<" "<<v.y<<" "<<v.r<<"\n";
}
