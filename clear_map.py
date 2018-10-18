# 碧蓝航线刷图脚本文件
# 针对3-4刷图
# 非酋出不了金皮，只能用脚本肝了T^T

import time
import cv2
import pyautogui
import numpy as np
from PIL import ImageGrab

# 获取当前屏幕截图
def get_current_screen():                                 
    img = ImageGrab.grab()
    img.save("current_screen.jpg")

    return np.asarray(img)


# 读取文件夹中事先保存的目标图片
def get_needed_img(filename):
    img = cv2.imread(filename)
    return np.asarray(img)


# 利用sift匹配图像，找到需要点击的坐标位置
def find_object_location(src, target):
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create()
    kpts1, descs1 = sift.detectAndCompute(src_gray, None)
    kpts2, descs2 = sift.detectAndCompute(target_gray, None)

    FLANN_INDEX_KDTREE = 1
    matcher = cv2.FlannBasedMatcher(dict(algorithm = FLANN_INDEX_KDTREE, trees = 4), {})

    # 选取匹配最相近的两个点
    matches = matcher.knnMatch(descs1, descs2, 2)
    # 按距离排序
    matches = sorted(matches, key = lambda x:x[0].distance)
    # 判断最优和次优匹配比率是否足够低，够低则匹配成功
    good = [m1 for (m1, m2) in matches if m1.distance < 0.68 * m2.distance]

    # 当有足够的健壮匹配点对（至少4个）时
    MIN_MATCH_COUNT = 5
    if len(good) >= MIN_MATCH_COUNT:
        # 从匹配中提取出对应点对
        dst_pts = np.float32([ kpts2[m.trainIdx].pt for m in good ]).reshape(-1,2)

        (x, y) = np.mean(dst_pts, axis=0)
        print(x, y)
        return (x,y)
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))
        return None, None


def get_image_location(template, img): 
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF)

    loc = np.where(res >= 0.9)

    # 遍历不同位置，绘制矩形
    # 在函数调用中使用*list/tuple，表示将list/tuple分开，作为位置参数传递给对应函数（前提是对应函数支持不定个数的位置参数）
    # 切片[::-1]是将列表或字符倒过来
    for pt in zip(*loc[::-1]):
        touch_loc = (pt[0] + w/2, pt[1] + h/2)
    #if np.where(res >= 0.8):
    #    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #    touch_loc = (max_loc[0] + w/2, max_loc[1] + h/2)

    #else:
    #   touch_loc = (None, None)

    return touch_loc



# 等待目标区域出现进行点击
def click_target_area_till_appear(filename):
    src = get_needed_img(filename)

    x = None
    while x == None:                                            # 如果没有捕捉到目标
        srceen = get_current_screen()                           # 可能是没有切到需要的页面
        x, y  = find_object_location(src, srceen)               # 重复检测，直到找到目标

    pyautogui.click(x, y)                                       # 点击目标


# 尝试性点击一次，没有目标则不点击
def click_target_area_once(filename):
    src = get_needed_img(filename)

    srceen = get_current_screen()                               # 获取当前界面
    x, y  = find_object_location(src, srceen)                  
    #x, y = get_image_location(src, srceen)
    print(filename, x, y)
    if x == None:                                               # 如果没有找到目标就不点击
        return 

    pyautogui.click(x, y)                                       # 点击目标


# 确定是否boss已经出现
def is_target_appear(filename):
    src = get_needed_img(filename)
    srceen = get_current_screen()                           
    x, y  = find_object_location(src, srceen)

    if x == None:
        return False, None, None
    else:
        return True, x, y          


# 自动刷图流程：选图 -> 选择舰队 -> 点选方块（优先boss）-> 出击 -> 等待结束，点击继续两次 -> 点击确定
if __name__ == "__main__":
    while(1):
        click_target_area_once("map3-4.jpg")
        time.sleep(.500)
        click_target_area_once("go_rightnow.jpg")
        time.sleep(.500)                                          # 要连续点击两次“立刻前往”，为了防止点击过快，加入延时
        click_target_area_once("go_rightnow.jpg")

        flag, x, y = is_target_appear("boss.jpg")
        if flag == True:
            pyautogui.click(x, y) 
            time.sleep(1.300)
        else:
            click_target_area_once("ship1.jpg")
            click_target_area_once("ship2.jpg")        
            click_target_area_once("ship3.jpg")
        

        click_target_area_once("attack.jpg")

        click_target_area_once("click2continue.jpg")
        time.sleep(.800)
        click_target_area_once("click2continue.jpg")
        time.sleep(2.8)

        click_target_area_once("confirm.jpg")


        
        



