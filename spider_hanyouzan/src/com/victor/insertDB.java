package com.victor;

import java.sql.*;
import java.util.concurrent.BlockingQueue;

/**
 * Created by Victor on 2015/4/25.
 */
public class insertDB implements Runnable {
    private BlockingQueue<Message> queue;
    Connection conn = null;
    Statement stat = null;
    ResultSet rs = null;
    int finished = 0; //终止变量

    public insertDB(BlockingQueue<Message> queue) throws ClassNotFoundException, SQLException {
        Class.forName("org.sqlite.JDBC");
        this.queue = queue;
    }

    @Override
    public void run() {
        while (true) {
            try {
                storage();
                if (this.finished != 0) {
                    break;
                }
            } catch (SQLException | ClassNotFoundException e) {
                e.printStackTrace();
            }
        }
    }

    public void setFinished(int finished) {
        this.finished = finished;
    }

    public void storage() throws SQLException, ClassNotFoundException {
        Message message = null;
        this.conn = DriverManager.getConnection("jdbc:sqlite:store1.db");
        this.stat = conn.createStatement();
        PreparedStatement prep = conn.prepareStatement("insert into main(time, website, html)values(?,?,?)");
        int quNum = queue.size();
        while (quNum < 50) {
            quNum = queue.size();
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            if (this.finished == 0) {   //最后不够50条一起处理
                quNum = queue.size();
                break;
            }
        }
        for (int i = 0; i <= quNum; i++) {  //一次插入50条数据
            try {
                message = queue.take();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            prep.setString(1, message.getTime());
            prep.setString(2, message.getWebsite());
            prep.setString(3, message.getHtml());
            prep.addBatch();
        }
        conn.setAutoCommit(false);
        prep.executeBatch();
        conn.setAutoCommit(true);
        this.conn.close();
    }

}
