package com.victor;

import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Created by Victor on 2015/4/25.
 */
public class Message {    //≈¿»°Õ¯“≥∂‘œÛ
    String website;
    String html;
    String time;

    public String getWebsite() {
        return website;
    }

    public String getHtml() {
        return html;
    }

    public String getTime() {
        return time;
    }

    public Message(String website,String html){
        this.website = website;
        this.html = html;
        Date nowTime;
        nowTime = new Date();
        SimpleDateFormat time=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        this.time =  time.format(nowTime);
    }

}
