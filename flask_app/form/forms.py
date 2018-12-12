# -*- coding: utf8 -*-
import sys
import time
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, MultipleFileField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, Email
from flask_ckeditor import CKEditorField

class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    save = SubmitField('Save')  # 保存按钮
    publish = SubmitField('Publish')  # 发布按钮”


class RichTextForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(1,50)])
    body = CKEditorField('body', validators=[DataRequired()])
    save = SubmitField('save')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('登录')


class UploadForm(FlaskForm):
    photo = FileField('upload images', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField()

class MultiUploadForm(FlaskForm):
    photo = MultipleFileField('upload images', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField()

class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit1 = SubmitField('Sign in')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit2 = SubmitField('Register')

class QueryTricket(FlaskForm):

    # my_choices = [('1', 'Choice1'), ('2', 'Choice2'), ('3', 'Choice3')]
    start_station = StringField('始发站', validators=[DataRequired(), Length(2, 8, message='请输入城市名')])
    end_station = StringField('到达站', validators=[DataRequired(), Length(2, 8, message='请输入城市名')])
    # times = DateField('乘车时间', validators=[DataRequired()])
    yuezhan_trains = StringField('越站车次')
    huancheng_num = StringField('换乘次数')
    # times = StringField('车次', validators=[DataRequired(), Length(min=10, max=10, message='输入格式：2018-11-08')])
    submit = SubmitField('查询')


if __name__ == '__main__':

    form = LoginForm()
    print form.username(style='width:200px', class_='bar')
    print form.password()
    print form.submit()
    print form.remember()