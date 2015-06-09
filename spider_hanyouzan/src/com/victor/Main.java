package com.victor;


import java.sql.SQLException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;

public class Main{

public static void main(String[] args) throws InterruptedException, SQLException, ClassNotFoundException {
        int mutLine1 = 40;

        BlockingQueue<Message> queue1 = new LinkedBlockingDeque<Message>();
        getdb getdb = new getdb(mutLine1,10000000,10000000 + 10000,queue1); //爬取前一万条
        insertDB insertdb = new insertDB(queue1);   //缓存下载的数据

        Thread[] t = new Thread[mutLine1];
        Thread t1 = new Thread(insertdb);
        for (int j = 0;j<mutLine1;j++){
            t[j] = new Thread(getdb);
        }
        for (int j = 0;j<mutLine1;j++) {
            t[j].start();
        }
        t1.start();
        for (int j = 0;j<mutLine1;j++){
            t[j].join();
        }
        insertdb.setFinished(1);    //告诉储存线程下载结束
        Thread.sleep(5000);       //给储存线程多5秒钟时间
        t1.join();

        ana ana1 = new ana();       //分析下载的数据
        Thread t2 = new Thread(ana1);
        t2.start();
        t2.join();
    }


}

