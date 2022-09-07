import deneyap
from machine import Pin, I2S
from wavlib import *
from audioconfig import *

ws_pin = Pin(deneyap.MICC)
sdin_pin = Pin(deneyap.MICD)

audio_in = I2S(
    I2S.NUM0, 
    ws=ws_pin, sdin=sdin_pin,
    standard=I2S.PHILIPS, 
    mode=I2S.MASTER_PDW,
    dataformat=I2S.B32,
    channelformat=I2S.RIGHT_LEFT,
    samplerate=SAMPLE_RATE,
    dmacount=50,
    dmalen=SAMPLES_DMA)

wav = open('rec.wav','wb')

wav_header = create_wav_header(
    SAMPLE_RATE, 
    WAV_SIZE, 
    CHANNELS, 
    SAMPLE_RATE * REC_TIME
)
num_bytes_written = wav.write(wav_header)

mic_samples = bytearray(MIC_BUFFER_SIZE)
mic_samples_mv = memoryview(mic_samples)
wav_samples = bytearray(MEM_BUFFER_SIZE)
wav_samples_mv = memoryview(wav_samples)

num_sample_bytes_written_to_wav = 0

print('Kayit basliyor..')

while num_sample_bytes_written_to_wav < NUM_BYTE_WRITE:
    try:
        num_bytes_read_from_mic = audio_in.readinto(mic_samples_mv, timeout=0)
        if num_bytes_read_from_mic > 0:
            num_bytes_snipped = snip_16_mono(mic_samples_mv[:num_bytes_read_from_mic], wav_samples_mv)
            num_bytes_to_write = min(num_bytes_snipped, NUM_BYTE_WRITE - num_sample_bytes_written_to_wav)
            num_bytes_written = wav.write(wav_samples_mv[:num_bytes_to_write])
            num_sample_bytes_written_to_wav += num_bytes_written
    except (KeyboardInterrupt, Exception) as e:
        print('Hata olustu {} {}'.format(type(e).__name__, e))
        break

wav.close()
audio_in.deinit()
print('Kayit Bitti..')
print('WAV dosyasına %d bit veri yazildi..' % num_sample_bytes_written_to_wav)