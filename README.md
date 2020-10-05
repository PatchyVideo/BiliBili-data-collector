# BiliBili-data-collector
帕琪站的B站东方up数据爬虫

主要是为<a href="https://space.bilibili.com/515657675/">帕琪站官方账号</a>的B站东方视频周报提供数据支持

## 项目构建

```bash
# 启动本项目前，需要保证后台运行项目PatchyVideo-textseg

# 拉取 PatchyVideo-textseg
$ git clone https://github.com/PatchyVideo/PatchyVideo-textseg
$ cd PatchyVideo-textseg

# 启动 PatchyVideo-textseg
$ go mod init PatchyVideo-textseg
$ go run main.go

# 拉取本项目
$ git clone https://github.com/PatchyVideo/BiliBili-data-collector
$ cd PatchyVideo-textseg

# 启动项目
$ python weekly_post.py
```

## 以后会完善的内容

- Excel文件写入（weekly_post_old.py里有加入，但是功能有待进一步改进）
- 数据库关联&API提供（考虑在做一个单独的前端页面来展示数据）