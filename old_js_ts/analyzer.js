"use strict";
// // search for email id in a specific visit 
// // search for email id accross visits 
// // report where it was shared 
// import { ReqType } from "./types";
// import * as ioredis from 'ioredis';
// let redis = new ioredis.Redis(); 
// function findEmail(aVisit: ReqType[]){
//     for (let aReq of aVisit){
//         if (JSON.stringify(aReq).match("a")){
//             // console.log(aReq);
//         }
//     }
// }
// let target = "http://gap.com"; 
// async function main(){
//     let log : ReqType[][][] = JSON.parse(await redis.call("JSON.GET", target, "$.log"));
//     console.log(log);
//     let log0 = log[0];
//     console.log(log);
//     console.log("==============================================================")
//     for (let visitList of log0){
//         console.log(visitList); 
//         console.log("---------------------")
//         findEmail(visitList); 
//     }
// }
// main(); 
