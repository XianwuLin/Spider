package com.victor;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.LinkedList;
import java.util.Queue;

/**
 * Created by Victor on 2015/4/26.
 */
public class ana implements  Runnable{
    FileOutputStream out = null;
    Queue<String[]> queue = null;

    public ana(Queue<String[]> queue, FileOutputStream out) {
        this.queue = queue;
        this.out = out;
    }


    public ana(){
        int mutLine2 = 4;
        try {
            Queue<String[]> queue = new LinkedList<String[]>();
            Class.forName("org.sqlite.JDBC");
            File f = new File("1.txt");
            if (f.exists()){
                f.delete();
            }
            f.createNewFile();
            FileOutputStream out = new FileOutputStream(f, true);
            Connection conn = DriverManager.getConnection("jdbc:sqlite:store1.db");
            Statement stat = conn.createStatement();
            ResultSet rs = null;
            String html,code,id = null,sql;
            sql = "select count(*) as rowcount from main;";
            rs = stat.executeQuery(sql);
            int number = rs.getInt("rowcount")  / 1000;
            ana runad = new ana(queue,out);
            Thread[] demo = new Thread[mutLine2];
            int i = 0;
            for (;i<=number;i+=1) {
                sql = "select * from main limit "+String.valueOf(i*1000)+",1000;";
                rs = stat.executeQuery(sql); //²éÑ¯Êý¾Ý
                System.out.println(String.valueOf(i*1000)+"\t\t\t\t\r");
                while (rs.next()) {
                    html = rs.getString("html");
                    code = rs.getString("website");
                    id = rs.getString("id");
                    queue.offer(new String[]{code, html, id});
                }
                for (int j = 0;j<mutLine2;j++){
                    demo[j] = new Thread(runad);
                }
                for (int j = 0;j<mutLine2;j++){
                    demo[j].start();
                }
                for (int j = 0;j<mutLine2;j++){
                    demo[j].join();
                }
            }
            rs.close();
            conn.close();
            out.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    String[] data = null;
    public String[] getData(){
        synchronized (this) {
            if (this.queue != null) {
                data = this.queue.poll();
            }
        }
        return data;
    }


    @Override
    public void run() {
        this.data = getData();
        while (this.data != null) {
            try {
                String code = this.data[0];
                String html = this.data[1];
                String id = this.data[2];
                Document doc = Jsoup.parse(html, "UTF-8");
                Elements contents = doc.getElementsByClass("prdTit");
                for (Element content : contents) {
                    String ctText = content.text();
                    String ut = code + "\t" + ctText + "\r\n";
                    synchronized (this) {
                        try {
                            this.out.write(ut.toString().getBytes("utf-8"));
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }
            } catch (Exception e) {
            }
            this.data = getData();
        }
    }
}
