import * as puppeteer from 'puppeteer';
import * as ioredis from 'ioredis';
import * as fs from "fs"; 
import type {ReqType} from "./types";
//  module load /opt/redis-stack/lib/rejson.so
const redis = new ioredis.Redis(); 

redis.call("JSON.SET", `all`, `$`, '{}');
const rawJson = fs.readFileSync("tranco.json");
const trancoJson = JSON.parse(rawJson.toString()); 

async function logSite( interceptedRequest : puppeteer.HTTPRequest){
    // console.log(interceptedRequest);
    console.log(interceptedRequest.url());
    console.log(interceptedRequest.headers());
    console.log(interceptedRequest.postData())
    // await redis.call("JSON.ARRAPPEND", 'all', `${category.replace(/[\s,\(,\),\\]/g, '')}.${site.replace(/[\s,\(,\),\\]/g, '')}`, `${interceptedRequest.url()}`);
}
// let target = "http://gap.com"; 
// let target = "http://text.npr.org"; 
let target = "https://www.washingtonpost.com"; 


let visitList : ReqType[] = []; // list of httpreq

async function run(){

    console.log(await redis.call("JSON.GET", target, "$")); 
    if (await redis.call("JSON.GET", target, "$") == null){
        await redis.call("JSON.SET", target, "$", '{"log":[]}'); 
    }
    const browser = await puppeteer.launch({headless: false});    
    let page = await browser.newPage();
    page.setRequestInterception(true);

    page.on("request", interceptedRequest => {

        if (interceptedRequest.isInterceptResolutionHandled() ) {
            logSite(interceptedRequest);  
            return;
        }
        else {
            // logSite(interceptedRequest);
            let aReq = {
                "header": interceptedRequest.headers(),
                "url" : interceptedRequest.url(),
                "post" : interceptedRequest.postData()
            };
            visitList.push(aReq); 
            // console.log("visitjsonsdfsdf")
            // console.log(visitList);
            interceptedRequest.continue();
        }
    });

    page.goto(target);
    page.on("close", _ => {
        console.log("closed");
        redis.call("JSON.ARRAPPEND", target, "$.log", JSON.stringify(visitList));
    });
    
}

run();