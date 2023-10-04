"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const puppeteer = __importStar(require("puppeteer"));
const ioredis = __importStar(require("ioredis"));
const fs = __importStar(require("fs"));
//  module load /opt/redis-stack/lib/rejson.so
const redis = new ioredis.Redis();
redis.call("JSON.SET", `all`, `$`, '{}');
const rawJson = fs.readFileSync("tranco.json");
const trancoJson = JSON.parse(rawJson.toString());
function logSite(interceptedRequest) {
    return __awaiter(this, void 0, void 0, function* () {
        // console.log(interceptedRequest);
        console.log(interceptedRequest.url());
        console.log(interceptedRequest.headers());
        console.log(interceptedRequest.postData());
        // await redis.call("JSON.ARRAPPEND", 'all', `${category.replace(/[\s,\(,\),\\]/g, '')}.${site.replace(/[\s,\(,\),\\]/g, '')}`, `${interceptedRequest.url()}`);
    });
}
// let target = "http://gap.com"; 
// let target = "http://text.npr.org"; 
let target = "https://www.washingtonpost.com";
let visitList = []; // list of httpreq
function run() {
    return __awaiter(this, void 0, void 0, function* () {
        console.log(yield redis.call("JSON.GET", target, "$"));
        if ((yield redis.call("JSON.GET", target, "$")) == null) {
            yield redis.call("JSON.SET", target, "$", '{"log":[]}');
        }
        const browser = yield puppeteer.launch({ headless: false });
        let page = yield browser.newPage();
        page.setRequestInterception(true);
        page.on("request", interceptedRequest => {
            if (interceptedRequest.isInterceptResolutionHandled()) {
                logSite(interceptedRequest);
                return;
            }
            else {
                // logSite(interceptedRequest);
                let aReq = {
                    "header": interceptedRequest.headers(),
                    "url": interceptedRequest.url(),
                    "post": interceptedRequest.postData()
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
    });
}
run();
