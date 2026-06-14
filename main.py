import pygame
import sounddevice as sd
import numpy as np
import sys
import random
# -- Cấu hình cơ bản --
WIDTH, HEIGHT = 800, 600
BLOW_THRESHOLD = 0.03  # Ngưỡng âm thanh để xác định là "thổi". (Giá trị từ 0.0 đến 1.0)
FPS = 60
# -- Định nghĩa các màu sắc sẽ sử dụng --
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CAKE_COLOR = (255, 182, 193)  # Màu bánh (LightPink)
ICING_COLOR = (255, 105, 180) # Màu kem phủ (HotPink)
PLATE_COLOR = (220, 220, 220) # Màu đĩa
CANDLE_COLOR = (173, 216, 230) # Màu thân nến (LightBlue)
FLAME_COLORS = [(255, 140, 0), (255, 215, 0), (255, 69, 0)] # Cam, Vàng, Đỏ cam
TEXT_COLOR = (255, 50, 50)
# Biến toàn cục để lưu trạng thái "đã thổi nến hay chưa"
is_blown = False
def audio_callback(indata, frames, time, status):
    """
    Hàm này được gọi liên tục bởi sounddevice để nhận dữ liệu âm thanh từ micro.
    """
    global is_blown
    if status:
        print(status, file=sys.stderr)
    
    # Tính độ lớn của âm thanh (RMS - Root Mean Square)
    volume_norm = np.linalg.norm(indata) * 10
    
    # Nếu âm lượng vượt qua ngưỡng cho phép, ta coi như nến đã được thổi
    if volume_norm > BLOW_THRESHOLD * 100:
        is_blown = True
def draw_cake(screen):
    """ Vẽ chiếc bánh kem và chiếc đĩa """
    # Vẽ đĩa hình oval ở dưới cùng
    plate_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 + 100, 400, 40)
    pygame.draw.ellipse(screen, PLATE_COLOR, plate_rect)
    
    # Vẽ thân bánh (hình chữ nhật)
    cake_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 120)
    pygame.draw.rect(screen, CAKE_COLOR, cake_rect, border_radius=10)
    
    # Vẽ lớp kem phủ bên trên
    icing_rect = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 - 10, 320, 40)
    pygame.draw.rect(screen, ICING_COLOR, icing_rect, border_radius=20)
    
    # Vẽ vài chi tiết trang trí (giọt kem chảy)
    for i in range(5):
        drop_x = WIDTH//2 - 140 + i * 70
        pygame.draw.circle(screen, ICING_COLOR, (drop_x, HEIGHT//2 + 25), 15)
def draw_candles(screen, num_candles, is_blown):
    """ Vẽ nến và ngọn lửa (nếu chưa thổi) """
    if num_candles <= 0:
        return
        
    start_x = WIDTH // 2 - 120
    end_x = WIDTH // 2 + 120
    
    # Tính khoảng cách giữa các ngọn nến để dàn đều trên bánh
    if num_candles == 1:
        step = 0
        start_x = WIDTH // 2
    else:
        step = (end_x - start_x) / (num_candles - 1)
        
    for i in range(num_candles):
        x = start_x + i * step
        y = HEIGHT // 2 - 60
        
        # Vẽ thân nến
        candle_rect = pygame.Rect(x - 6, y, 12, 50)
        pygame.draw.rect(screen, CANDLE_COLOR, candle_rect, border_radius=3)
        
        # Vẽ bấc nến (đoạn dây đen nhỏ)
        pygame.draw.line(screen, BLACK, (x, y), (x, y - 5), 2)
        
        # Nếu chưa thổi nến thì vẽ ngọn lửa
        if not is_blown:
            # Chọn màu ngẫu nhiên cho lửa để tạo cảm giác bập bùng
            flame_color = random.choice(FLAME_COLORS)
            # Thay đổi kích thước/vị trí lửa ngẫu nhiên một chút xíu
            offset_y = random.randint(-2, 2)
            pygame.draw.ellipse(screen, flame_color, (x - 8, y - 25 + offset_y, 16, 25))
def main():
    global is_blown
    
    # 1. Nhập thông tin Tên và Tuổi qua Console
    print("\n" + "="*40)
    print("🎂 CHƯƠNG TRÌNH BÁNH SINH NHẬT BẰNG PYTHON 🎂")
    print("="*40)
    
    try:
        age_input = input(">> Nhập số tuổi của bạn (tương ứng số nến): ")
        age = int(age_input)
    except ValueError:
        print(">> Lỗi: Số tuổi phải là số! Mình sẽ để mặc định là 1 nến nhé.")
        age = 1
        
    name = input(">> Nhập tên của bạn (hoặc người nhận): ")
    
    print("\n" + "="*40)
    print(">> Đang mở cửa sổ bánh kem...")
    print(">> HƯỚNG DẪN: Hãy đưa miệng gần micro của máy tính và THỔI MẠNH để tắt nến nhé!")
    print("="*40 + "\n")
    
    # 2. Khởi tạo Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Happy Birthday Cake")
    clock = pygame.time.Clock()
    
    # Font chữ cho lời chúc
    # Có thể dùng None để lấy font mặc định, kích thước 64
    try:
        font = pygame.font.SysFont("comicsansms", 64, bold=True)
    except:
        font = pygame.font.Font(None, 64)
    
    # 3. Mở luồng lắng nghe âm thanh từ Micro
    # Lắng nghe 1 kênh (mono)
    try:
        stream = sd.InputStream(channels=1, callback=audio_callback)
        stream.start()
    except Exception as e:
        print(f"Không thể mở Microphone: {e}")
        print("Nến sẽ tự động tắt sau 5 giây nếu không có micro!")
        stream = None
    
    # Khởi tạo thời gian (dùng cho trường hợp không có micro)
    start_ticks = pygame.time.get_ticks()
    
    # 4. Vòng lặp chính của giao diện
    running = True
    while running:
        # Xử lý sự kiện (ví dụ: người dùng bấm dấu X để đóng)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Trường hợp máy không có micro/lỗi micro: tự tắt nến sau 5 giây
        if stream is None and not is_blown:
            seconds = (pygame.time.get_ticks() - start_ticks) / 1000
            if seconds > 5:
                is_blown = True
                
        # Xóa màn hình bằng màu trắng
        screen.fill(WHITE)
        
        # Vẽ bánh và nến
        draw_cake(screen)
        draw_candles(screen, age, is_blown)
        
        # Nếu nến đã tắt, hiển thị dòng chữ chúc mừng
        if is_blown:
            text_str = f"Happy Birthday {name}!"
            text_surface = font.render(text_str, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
            screen.blit(text_surface, text_rect)
            
        # Cập nhật màn hình
        pygame.display.flip()
        
        # Khống chế tốc độ khung hình (FPS)
        clock.tick(FPS)
        
    # Kết thúc chương trình, dọn dẹp bộ nhớ
    if stream is not None:
        stream.stop()
        stream.close()
    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()
