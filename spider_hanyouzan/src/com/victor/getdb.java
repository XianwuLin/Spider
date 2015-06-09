package com.victor;

import org.apache.http.HttpEntity;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.concurrent.BlockingQueue;

;

/**
 * Created by Victor on 2015/4/25.
 */
public class getdb implements Runnable {
    private BlockingQueue<Message> queue;
    int mutLine = 40;  //40个线程
    int Num,Max;
    Message message = null;
    public getdb(int mutLine,int Num, int Max,BlockingQueue<Message> queue){
        this.Num = Num;
        this.Max = Max;
        this.queue = queue;
        try {
            this.mutLine = mutLine;
            createDb();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public int getNum(){   //分发下一个数字
        synchronized (this) {
            this.Num += 1;
            System.out.print("Download:\t" + String.valueOf((this.Num - this.mutLine)-10000000) + "\r");
            if (this.Num > Max){
                return 0;
            }else{
                return this.Num;
            }
        }
    }

    @Override
    public void run() {
        int localNum = getNum();
        while(localNum > 0) {
            String html = null;
            CloseableHttpClient httpClient = HttpClients.createDefault();
            String url = "http://www.hanyouzan.com/display/goods.do?goods_code=" + String.valueOf(localNum);
            final RequestConfig params = RequestConfig.custom().setConnectTimeout(10000).setSocketTimeout(10000).build();
            final HttpGet httpget = new HttpGet(url);
            httpget.setConfig(params);
            try {
                final CloseableHttpResponse response = httpClient.execute(httpget);
                HttpEntity entity = response.getEntity();
                html = EntityUtils.toString(entity);
                message = new Message(String.valueOf(localNum),html);
                queue.put(message); //放入缓存
                response.close();
            } catch (Exception e) {
                //e.printStackTrace();
                System.out.println(String.valueOf(localNum) + "Retry\t\t\t");
                continue;
            }

            localNum = getNum();
        }

    }

    public  void createDb() throws ClassNotFoundException, SQLException {  //创建数据库
        Class.forName("org.sqlite.JDBC");
        Connection conn = DriverManager.getConnection("jdbc:sqlite:store1.db");
        Statement stat = conn.createStatement();
        stat.executeUpdate("drop table if exists main;");
        stat.executeUpdate("create table main(id INTEGER PRIMARY KEY " +
                "AUTOINCREMENT, time TEXT, website BLOB, html TEXT);");
        conn.close();
    }

}
