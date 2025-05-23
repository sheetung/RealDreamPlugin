from PIL import Image, ImageDraw, ImageFont
import os

class ImageTextEditor:
    def __init__(self, image_path, output_path, font_path, out_img_name):
        """
        初始化图片编辑器
        :param image_path: 输入图片路径
        :param output_path: 输出图片路径
        :param font_path: 字体文件路径
        """
        self.image_path = self._get_absolute_path(image_path)
        self.output_path = self._get_absolute_path(output_path)
        self.font_path = self._get_absolute_path(font_path)
        # 验证关键路径
        self._validate_paths()
        
    
        # 默认参数配置
        self.default_config = {
            'text': "默认文本\n第二行",
            'position': (50, 50),  # (x, y)
            'font_size_ratio': 0.05,
            'line_spacing': 1.2,
            'bg_padding': 10,
            'bg_color': (0, 0, 0, 100),
            'text_color': (255, 255, 255, 230)
        }
        
        # 运行时参数
        self.current_image = None
        self.custom_font = None

    def _get_absolute_path(self, path):
        """将路径转换为绝对路径并标准化"""
        # 处理路径中的 ~ 符号
        expanded_path = os.path.expanduser(path)
        # 转换为绝对路径
        abs_path = os.path.abspath(expanded_path)
        # 标准化路径分隔符
        return os.path.normpath(abs_path)
    
    def _validate_paths(self):
        """验证关键文件路径是否存在"""
        # 检查输入图片
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"输入图片不存在: {self.image_path}")
            
        # 检查字体文件
        if not os.path.isfile(self.font_path):
            raise FileNotFoundError(f"字体文件不存在: {self.font_path}")
            
        # 自动创建输出目录
        output_dir = os.path.dirname(self.output_path)
        os.makedirs(output_dir, exist_ok=True)

    def configure_text(self, text=None, position=None, **kwargs):
        """
        配置文本参数
        :param text: 要添加的文本内容
        :param position: 文本起始坐标(x, y)
        :param kwargs: 可覆盖其他默认配置参数
        """
        self.current_config = self.default_config.copy()
        
        # 更新配置参数
        if text is not None:
            self.current_config['text'] = text
        if position is not None:
            self.current_config['position'] = position
        self.current_config.update(kwargs)

    def _load_font(self, img_width, img_height):
        """
        加载自定义字体
        """
        try:
            if not os.path.exists(self.font_path):
                raise FileNotFoundError(f"字体文件不存在：{self.font_path}")
            
            # 动态计算字体大小
            base_size = min(img_width, img_height)
            font_size = int(base_size * self.current_config['font_size_ratio'])
            
            self.custom_font = ImageFont.truetype(self.font_path, size=font_size)
        except Exception as e:
            print(f"字体加载失败，使用默认字体：{str(e)}")
            self.custom_font = ImageFont.load_default()

    def _calculate_text_area(self, draw):
        """
        计算文本区域尺寸
        """
        return draw.multiline_textbbox(
            self.current_config['position'],
            self.current_config['text'],
            font=self.custom_font,
            spacing=int(self.custom_font.size * self.current_config['line_spacing'])
        )

    def _create_background_layer(self, text_bbox):
        """
        创建半透明背景层
        """
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        padding = self.current_config['bg_padding']
        
        bg_layer = Image.new('RGBA', 
                            (text_width + 2*padding, text_height + 2*padding),
                            self.current_config['bg_color'])
        return bg_layer

    def process_image(self):
        """
        执行图片处理流程
        """
        try:
            # 打开并转换图片模式
            self.current_image = Image.open(self.image_path).convert("RGBA")
            draw = ImageDraw.Draw(self.current_image)
            
            # 加载字体
            self._load_font(*self.current_image.size)
            
            # 计算文本区域
            text_bbox = self._calculate_text_area(draw)
            
            # 创建并粘贴背景层
            bg_layer = self._create_background_layer(text_bbox)
            paste_position = (
                self.current_config['position'][0] - self.current_config['bg_padding'],
                self.current_config['position'][1] - self.current_config['bg_padding']
            )
            self.current_image.paste(bg_layer, paste_position, bg_layer)
            
            # 绘制文本
            draw.multiline_text(
                xy=self.current_config['position'],
                text=self.current_config['text'],
                fill=self.current_config['text_color'],
                font=self.custom_font,
                spacing=int(self.custom_font.size * self.current_config['line_spacing']),
                align="left"
            )
            
            # 保存结果
            self.current_image.convert("RGB").save(self.output_path)
            print(f"处理成功，图片已保存至：{self.output_path}")
            return True
            
        except Exception as e:
            print(f"图片处理失败：{str(e)}")
            return False

# 使用示例
if __name__ == "__main__":
    # 初始化编辑器
    editor_cross = ImageTextEditor(
        image_path=os.path.join('PILimg',"tool", "img"),
        output_path=os.path.join('PILimg', "output"),
        font_path=os.path.join('PILimg',"tool", "font", "SourceHanSansSC-VF.ttf"),
        out_img_name='result.png'
    )
    
    # 配置文本参数
    editor_cross.configure_text(
        text="运势\n今日大吉大吉大吉大吉",
        position=(100, 200),  # 设置文本位置
        font_size_ratio=0.06,  # 调大字号ao'ao
        bg_color=(0, 100, 200, 150)  # 修改背景颜色
    )
    
    # 执行处理
    editor_cross.process_image()
