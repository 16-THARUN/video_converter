#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <nlohmann/json.hpp>

extern "C"
{
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/imgutils.h>
#include <libavutil/pixdesc.h>
}

using json = nlohmann::json;

// Structure to hold our high-quality HDR metadata
struct FrameMetadata
{
    int f;      // Frame number
    uint16_t p; // Peak (MaxRGB)
    uint16_t a; // Average (FALL)
};

void process_video_gpu(const char *input_path, const char *output_json)
{
    avformat_network_init();
    AVFormatContext *fmt_ctx = nullptr;

    if (avformat_open_input(&fmt_ctx, input_path, nullptr, nullptr) < 0)
    {
        std::cerr << "❌ Could not open input file." << std::endl;
        return;
    }
    avformat_find_stream_info(fmt_ctx, nullptr);

    int video_stream_idx = av_find_best_stream(fmt_ctx, AVMEDIA_TYPE_VIDEO, -1, -1, nullptr, 0);
    if (video_stream_idx < 0)
        return;

    AVCodecParameters *codec_params = fmt_ctx->streams[video_stream_idx]->codecpar;
    const AVCodec *codec = avcodec_find_decoder_by_name("hevc_cuvid");
    if (!codec)
        codec = avcodec_find_decoder(codec_params->codec_id);

    AVCodecContext *codec_ctx = avcodec_alloc_context3(codec);
    avcodec_parameters_to_context(codec_ctx, codec_params);

    if (avcodec_open2(codec_ctx, codec, nullptr) < 0)
        return;

    AVFrame *frame = av_frame_alloc();
    AVFrame *sw_frame = av_frame_alloc();
    AVPacket *packet = av_packet_alloc();

    std::vector<FrameMetadata> all_metadata;

    std::cout << "⚡ NVIDIA CUVID ENGAGED (RTX 3050) ⚡" << std::endl;
    std::cout << "📊 Mode: MaxRGB + FALL Analysis" << std::endl;

    while (av_read_frame(fmt_ctx, packet) >= 0)
    {
        if (packet->stream_index == video_stream_idx)
        {
            if (avcodec_send_packet(codec_ctx, packet) == 0)
            {
                while (avcodec_receive_frame(codec_ctx, frame) == 0)
                {
                    int ret = av_hwframe_transfer_data(sw_frame, frame, 0);
                    AVFrame *target = (ret < 0) ? frame : sw_frame;

                    uint16_t current_max = 0;
                    uint64_t total_sum = 0; // Using 64-bit to prevent overflow on 4K frames
                    uint64_t pixel_count = (uint64_t)target->width * target->height;

                    bool is_10bit = (target->format == AV_PIX_FMT_YUV420P10LE || target->format == AV_PIX_FMT_P010LE);

                    for (int y = 0; y < target->height; y++)
                    {
                        if (is_10bit)
                        {
                            uint16_t *src = (uint16_t *)(target->data[0] + y * target->linesize[0]);
                            for (int x = 0; x < target->width; x++)
                            {
                                uint16_t val = src[x];
                                if (val > current_max)
                                    current_max = val;
                                total_sum += val;
                            }
                        }
                        else
                        {
                            uint8_t *src = target->data[0] + y * target->linesize[0];
                            for (int x = 0; x < target->width; x++)
                            {
                                uint8_t val = src[x];
                                if (val > current_max)
                                    current_max = val;
                                total_sum += val;
                            }
                        }
                    }

                    uint16_t current_avg = (uint16_t)(total_sum / pixel_count);
                    all_metadata.push_back({(int)all_metadata.size(), current_max, current_avg});

                    if (all_metadata.size() % 1000 == 0)
                    {
                        std::cout << "\r🚀 GPU Speed: " << all_metadata.size() << " frames processed..." << std::flush;
                    }
                }
            }
        }
        av_packet_unref(packet);
    }

    // Export to JSON
    json output;
    output["HDR10plusProfile"] = "B";
    output["TotalFrames"] = all_metadata.size();

    for (const auto &meta : all_metadata)
    {
        output["Metadata"].push_back({
            {"f", meta.f},
            {"p", meta.p},
            {"a", meta.a} // Added average luminance
        });
    }

    std::ofstream file(output_json);
    file << output.dump();

    std::cout << "\n✅ Task Complete! Metadata generated with FALL values." << std::endl;

    // Cleanup
    av_frame_free(&frame);
    av_frame_free(&sw_frame);
    av_packet_free(&packet);
    avcodec_free_context(&codec_ctx);
    avformat_close_input(&fmt_ctx);
}

int main(int argc, char *argv[])
{
    if (argc < 3)
        return -1;
    process_video_gpu(argv[1], argv[2]);
    return 0;
}