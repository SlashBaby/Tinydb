from django.db import models

# Create your models here.
#用户信息模型
class Users(models.Model):
    sid = models.CharField(max_length=50)
    password = models.CharField(max_length=45)
    state = models.IntegerField(default=1)

    def toDict(self):
    	return {'id':self.id, 'sid':self.sid, 'password': self.password, 'state': self.state}

    class Meta:
        db_table = "users"  # 更改表名

class Tests(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField()
    answer = models.TextField()
    index = models.IntegerField(default=11)

    def toDict(self):
    	return {'content':self.content, 'answer': self.answer}

    class Meta:
        db_table = "tests"  # 更改表名