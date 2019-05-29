 #!/bin/bash
  2 callID=`date +%s%N`
  3 read -p "请输入意图缩写(默认：MK01)：" intent
  4 read -p "请输入预测文本(默认：对 对 对 。 我 你 找 我 有 什么 事 啊)：" text
  5
  6 if [ -z $intent ]
  7 then
  8     intent="MK01"
  9 fi
 10
 11 if [ -z $text ]
 12 then
 13     text="对 对 对 。 我 你 找 我 有 什么 事 啊"
 14 fi
 15
 16 timestamp=`date +%Y-%m-%d-%H-%M-%S`
 17
 18 start=`date +%s%N`
 19 result1=$(curl -H "Content-type: application/json" -X POST -s -d "{\"callID\":\"$callID\",\"timestamp\":\"$timestamp\",\"type\":\"normal\",\"text\":\"$intent\"}" 192.168.130.3:8989/HejunHuaShu)
 20 huashu_end=`date +%s%N`
 21 result2=$(curl -H "Content-type: application/json" -X POST -s -d "{\"callId\":\"${callID}\",\"text\":\"${text}\"}" 192.168.130.3:8989/text/uploader)
 22 intent_end=`date +%s%N`
 23
 24 huashu_time=`expr $huashu_end - $start`
 25 huashu_time=`expr $huashu_time / 1000000`
 26 intent_time=`expr $intent_end - $huashu_end`
 27 intent_time=`expr $intent_time / 1000000`
 28
 29
 30 echo -e "话术输入请求：curl -H \"Content-type: application/json\" -X POST -s -d \"{"callID":"$callID","timestamp":"$timestamp","type":"normal","text":"$intent"}\" 192.168.130.3:8989/HejunHuaShu \n"
 31 echo -e "响应结果：$result1 \n"
 32 echo -e "话术输入接口响应时间：$huashu_time ms \n"
 33 echo -e "文本上传请求：curl -H \"Content-type: application/json\" -X POST -s -d \"{"callId":"${callID}","text":"${text}"}\" 192.168.130.3:8989/text/uploader \n"
 34 echo -e "响应结果：$result2 \n"
 35 echo -e "文本输入接口响应时间：$intent_time ms \n"