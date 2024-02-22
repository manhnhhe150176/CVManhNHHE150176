from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from keras.models import load_model
import numpy as np
import keras
from kivy.utils import platform
from PIL import Image
import json
from kivy.config import Config

Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '850')

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.CAMERA])


Builder.load_file('frontend.kv')
DATA = json.load(open('data.json', encoding="utf8"))
OTHER = 42


class CameraScreen(Screen):
    def capture(self):
        self.texture = self.ids.camera.texture
        self.ids.camera.play = False
        self.ids.capture.disabled = True
        
        self.texture.blit_buffer(self.texture.pixels, colorfmt='rgba', bufferfmt='ubyte')
        self.pil_image = Image.frombytes("RGBA", size=self.texture.size, data=self.texture.pixels)
        self.pil_image = self.pil_image.convert('RGB').resize((224,224))
        self.id_food = self.load_model(self.pil_image)
        
        if self.id_food == OTHER:
            self.ids.restart_camera.disabled = False
            self.manager.current_screen.ids.name_food.text = "!!! Lỗi !!!"
            self.manager.current_screen.ids.name_food.color = 1,0,0,1
            self.manager.current_screen.ids.infomation_food.text = "Vật phẩm bạn đã chụp, tôi không thể nhận ra do chưa có dữ liệu trong thư viện."
            self.manager.current_screen.ids.infomation_food.color = 1,0,0,1
        else:
            self.ids.restart_camera.disabled = False
            self.ids.recognition_food.disabled = False
            for info_food in DATA['DataOfFood']:
                if info_food['ID'] == self.id_food:
                    self.manager.current_screen.ids.name_food.text = info_food['Name']
                    self.manager.current_screen.ids.name_food.color = 0,0,0,1
                    self.manager.current_screen.ids.infomation_food.text = info_food['Information']
                    self.manager.current_screen.ids.infomation_food.color = 0,0,0,1
                
        
    def restart(self):
        self.ids.camera.play = True
        self.ids.camera.texture = None
        self.ids.recognition_food.disabled = True
        self.ids.restart_camera.disabled = True
        self.ids.capture.disabled = False
        self.manager.current_screen.ids.name_food.text = ""
        self.manager.current_screen.ids.infomation_food.text = ""        
           

    def next(self):
        self.manager.current = 'nutrition_info_screen'
        self.manager.current_screen.ids.img.texture = self.texture
        for info_food in DATA['DataOfFood']:
            if info_food['ID'] == self.id_food:
                nutrition_info = info_food["NutritionInfo"]
                self.manager.current_screen.ids.nutrition_info.text = nutrition_info['Info']
                text_nutrition = ""
                for text in nutrition_info['Nutrition']:
                    text_nutrition = text_nutrition + "    * " + text + "\n"
                self.manager.current_screen.ids.nutrition.text = text_nutrition
    
    def load_model(self, img):
        img_arr = keras.preprocessing.image.img_to_array(img)
        img_arr_expnd  = np.expand_dims(img_arr,axis=0)
        img = keras.applications.mobilenet_v3.preprocess_input(img_arr_expnd)
        pred = model.predict(img)
        classes = ['Banh bao', 'Banh beo', 'Banh bot loc', 'Banh can', 'Banh canh', 'Banh chung', 'Banh cuon', 'Banh da', 'Banh day', 'Banh duc', 'Banh gio', 'Banh goi', 'Banh khot', 'Banh mi', 'Banh pia', 'Banh tet', 'Banh trang nuong', 'Banh xeo', 'Bun bo Hue', 'Bun dau mam tom', 'Bun mam', 'Bun rieu', 'Bun thit nuong', 'Ca kho to', 'Canh chua', 'Canh cua', 'Cao lau', 'Cha muc', 'Chao long', 'Com tam', 'Doi', 'Ga luoc', 'Gio lua', 'Goi cuon', 'Hu tieu', 'Keo lac', 'Khoai nuong', 'Mi quang', 'Muc chien', 'Nem', 'Nem chua', 'Ngo', 'Other', 'Pho', 'Pho cuon', 'Thit kho tau', 'Thit xien', 'Trau gac bep', 'Trung vit lon', 'Vit quay', 'Xoi xeo']
        print(classes[np.argmax(pred)])
        result = np.argmax(pred)
        return result


class NutritionInfoScreen(Screen):
    def back_to_menu(self):
        self.manager.current = 'camera_screen'
        
    def next_to_cooking(self):
        self.manager.current = 'cooking_instructions_screen'
        id_food = App.get_running_app().root.ids.camera_screen.id_food
        for info_food in DATA['DataOfFood']:
            if info_food['ID'] == id_food:
                coooking_instructions = info_food['CoookingInstructions']
                string = "[b]Ingredient[/b]" + "\n" 
                string = string + coooking_instructions['Ingredient'] + "\n"+ "\n"
                string = string + "[b]Time[/b]" + "\n" 
                string = string + coooking_instructions['Time'] + "\n" + "\n"
                string = string + "[b]Cooking[/b]" + "\n" 
                step_cooking = ""
                for step in coooking_instructions['Cooking']:
                    step_cooking = step_cooking + step + "\n"
                string = string + step_cooking + "\n"
                self.manager.current_screen.ids.ingredient_cooking.text = string
        
class CookingInstructionsScreen(Screen):
    def back_to_nutrition_info(self):
        self.manager.current = 'nutrition_info_screen'
        
    def back_to_menu(self):
        self.manager.current = 'camera_screen'
 
    
class RootWidget(ScreenManager):
    pass

class AIFood(App):
    def build(self):
        return RootWidget()
    



if __name__ == "__main__":
    # tensorflow.lite.TFLiteConverter.
    model = load_model("model_mobileNetV3.h5")
    app = AIFood()
    app.run()
    
