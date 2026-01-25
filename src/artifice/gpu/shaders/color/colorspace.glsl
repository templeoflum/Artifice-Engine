#version 430

// Color Space Conversion compute shader
// Converts between all 16 GLIC color spaces
//
// Color spaces and their characteristics:
//
// Perceptual (good for gradients):
// - LAB: Perceptually uniform, excellent for color manipulation
// - LUV: Similar to LAB, better for additive color
// - HCL: Cylindrical LAB, intuitive hue control
//
// Video/Compression:
// - YCbCr: JPEG/MPEG standard, separates luma from chroma
// - YUV: Analog video standard
// - YPbPr: Component video
// - YDbDr: SECAM video
//
// Artist-Friendly:
// - HSV/HSB: Intuitive hue/saturation/brightness
// - HSL: Similar but different lightness model
// - HWB: Hue/whiteness/blackness (CSS standard)
//
// Scientific:
// - XYZ: CIE 1931, device-independent
// - YXY: Chromaticity diagram coordinates
//
// Special:
// - CMY: Subtractive color (print)
// - OHTA: Optimal color features
// - GREY: Grayscale (luma only)
//
// Glitch effects work best by processing in a luma-chroma space
// (YCbCr, LAB) then corrupting the chroma channels while
// preserving luma for structure.

layout(local_size_x = 16, local_size_y = 16, local_size_z = 1) in;

// Input/output images
layout(rgba32f, binding = 0) readonly uniform image2D input_image;
layout(rgba32f, binding = 1) writeonly uniform image2D output_image;

// Parameters
uniform int from_space;  // Source color space
uniform int to_space;    // Target color space

// Color space IDs - all 16 GLIC color spaces
#define CS_RGB    0
#define CS_HSV    1
#define CS_HSL    2
#define CS_YCbCr  3
#define CS_YUV    4
#define CS_LAB    5
#define CS_XYZ    6
#define CS_LUV    7
#define CS_HCL    8
#define CS_CMY    9
#define CS_HWB    10
#define CS_YPbPr  11
#define CS_YDbDr  12
#define CS_OHTA   13
#define CS_YXY    14
#define CS_GREY   15

// D65 reference white
const vec3 D65 = vec3(0.95047, 1.0, 1.08883);

const float PI = 3.14159265359;

// ============================================================================
// Utility functions
// ============================================================================

// Linearize sRGB
float srgb_to_linear(float c) {
    return c <= 0.04045 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4);
}

// Apply sRGB gamma
float linear_to_srgb(float c) {
    return c <= 0.0031308 ? c * 12.92 : 1.055 * pow(c, 1.0/2.4) - 0.055;
}

vec3 linearize_rgb(vec3 rgb) {
    return vec3(
        srgb_to_linear(rgb.r),
        srgb_to_linear(rgb.g),
        srgb_to_linear(rgb.b)
    );
}

vec3 gamma_rgb(vec3 linear) {
    return vec3(
        linear_to_srgb(linear.r),
        linear_to_srgb(linear.g),
        linear_to_srgb(linear.b)
    );
}

// LAB helper functions
float lab_f(float t) {
    const float delta = 6.0/29.0;
    return t > delta*delta*delta
        ? pow(t, 1.0/3.0)
        : t / (3.0*delta*delta) + 4.0/29.0;
}

float lab_f_inv(float t) {
    const float delta = 6.0/29.0;
    return t > delta
        ? t*t*t
        : 3.0*delta*delta * (t - 4.0/29.0);
}

// ============================================================================
// RGB <-> HSV
// ============================================================================

vec3 rgb_to_hsv(vec3 rgb) {
    float M = max(max(rgb.r, rgb.g), rgb.b);
    float m = min(min(rgb.r, rgb.g), rgb.b);
    float C = M - m;

    float h = 0.0;
    if (C > 0.0001) {
        if (M == rgb.r) {
            h = mod((rgb.g - rgb.b) / C, 6.0);
        } else if (M == rgb.g) {
            h = (rgb.b - rgb.r) / C + 2.0;
        } else {
            h = (rgb.r - rgb.g) / C + 4.0;
        }
        h /= 6.0;
    }

    float s = (M > 0.0001) ? C / M : 0.0;
    float v = M;

    return vec3(h, s, v);
}

vec3 hsv_to_rgb(vec3 hsv) {
    float h = hsv.x * 6.0;
    float s = hsv.y;
    float v = hsv.z;

    float C = v * s;
    float X = C * (1.0 - abs(mod(h, 2.0) - 1.0));
    float m = v - C;

    vec3 rgb;
    if (h < 1.0) rgb = vec3(C, X, 0.0);
    else if (h < 2.0) rgb = vec3(X, C, 0.0);
    else if (h < 3.0) rgb = vec3(0.0, C, X);
    else if (h < 4.0) rgb = vec3(0.0, X, C);
    else if (h < 5.0) rgb = vec3(X, 0.0, C);
    else rgb = vec3(C, 0.0, X);

    return rgb + m;
}

// ============================================================================
// RGB <-> HSL
// ============================================================================

vec3 rgb_to_hsl(vec3 rgb) {
    float M = max(max(rgb.r, rgb.g), rgb.b);
    float m = min(min(rgb.r, rgb.g), rgb.b);
    float C = M - m;
    float L = (M + m) / 2.0;

    float h = 0.0;
    if (C > 0.0001) {
        if (M == rgb.r) {
            h = mod((rgb.g - rgb.b) / C, 6.0);
        } else if (M == rgb.g) {
            h = (rgb.b - rgb.r) / C + 2.0;
        } else {
            h = (rgb.r - rgb.g) / C + 4.0;
        }
        h /= 6.0;
    }

    float s = (L > 0.0001 && L < 0.9999) ? C / (1.0 - abs(2.0 * L - 1.0)) : 0.0;

    return vec3(h, s, L);
}

vec3 hsl_to_rgb(vec3 hsl) {
    float h = hsl.x * 6.0;
    float s = hsl.y;
    float L = hsl.z;

    float C = (1.0 - abs(2.0 * L - 1.0)) * s;
    float X = C * (1.0 - abs(mod(h, 2.0) - 1.0));
    float m = L - C / 2.0;

    vec3 rgb;
    if (h < 1.0) rgb = vec3(C, X, 0.0);
    else if (h < 2.0) rgb = vec3(X, C, 0.0);
    else if (h < 3.0) rgb = vec3(0.0, C, X);
    else if (h < 4.0) rgb = vec3(0.0, X, C);
    else if (h < 5.0) rgb = vec3(X, 0.0, C);
    else rgb = vec3(C, 0.0, X);

    return rgb + m;
}

// ============================================================================
// RGB <-> XYZ (sRGB with D65 illuminant)
// ============================================================================

vec3 rgb_to_xyz(vec3 rgb) {
    vec3 linear = linearize_rgb(rgb);

    // RGB to XYZ matrix (sRGB, D65)
    mat3 M = mat3(
        0.4124564, 0.3575761, 0.1804375,
        0.2126729, 0.7151522, 0.0721750,
        0.0193339, 0.1191920, 0.9503041
    );

    return M * linear;
}

vec3 xyz_to_rgb(vec3 xyz) {
    // XYZ to RGB matrix (sRGB, D65)
    mat3 M = mat3(
         3.2404542, -1.5371385, -0.4985314,
        -0.9692660,  1.8760108,  0.0415560,
         0.0556434, -0.2040259,  1.0572252
    );

    vec3 linear = M * xyz;
    return gamma_rgb(clamp(linear, 0.0, 1.0));
}

// ============================================================================
// RGB <-> LAB (CIE L*a*b*)
// ============================================================================

vec3 rgb_to_lab(vec3 rgb) {
    vec3 xyz = rgb_to_xyz(rgb);

    float fx = lab_f(xyz.x / D65.x);
    float fy = lab_f(xyz.y / D65.y);
    float fz = lab_f(xyz.z / D65.z);

    float L = 116.0 * fy - 16.0;
    float a = 500.0 * (fx - fy);
    float b = 200.0 * (fy - fz);

    // Normalize to [0,1] range for storage
    return vec3(L / 100.0, (a + 128.0) / 255.0, (b + 128.0) / 255.0);
}

vec3 lab_to_rgb(vec3 lab) {
    // Denormalize from [0,1]
    float L = lab.x * 100.0;
    float a = lab.y * 255.0 - 128.0;
    float b = lab.z * 255.0 - 128.0;

    float fy = (L + 16.0) / 116.0;
    float fx = a / 500.0 + fy;
    float fz = fy - b / 200.0;

    vec3 xyz = vec3(
        D65.x * lab_f_inv(fx),
        D65.y * lab_f_inv(fy),
        D65.z * lab_f_inv(fz)
    );

    return xyz_to_rgb(xyz);
}

// ============================================================================
// RGB <-> LUV (CIE L*u*v*)
// ============================================================================

vec3 rgb_to_luv(vec3 rgb) {
    vec3 xyz = rgb_to_xyz(rgb);

    float denom = xyz.x + 15.0 * xyz.y + 3.0 * xyz.z;
    float u_prime = (denom > 0.0001) ? (4.0 * xyz.x) / denom : 0.0;
    float v_prime = (denom > 0.0001) ? (9.0 * xyz.y) / denom : 0.0;

    // Reference white u', v'
    float denom_n = D65.x + 15.0 * D65.y + 3.0 * D65.z;
    float u_prime_n = (4.0 * D65.x) / denom_n;
    float v_prime_n = (9.0 * D65.y) / denom_n;

    float yr = xyz.y / D65.y;
    float L = yr > 0.008856 ? 116.0 * pow(yr, 1.0/3.0) - 16.0 : 903.3 * yr;
    float u = 13.0 * L * (u_prime - u_prime_n);
    float v = 13.0 * L * (v_prime - v_prime_n);

    // Normalize to [0,1] range
    return vec3(L / 100.0, (u + 100.0) / 200.0, (v + 100.0) / 200.0);
}

vec3 luv_to_rgb(vec3 luv) {
    // Denormalize
    float L = luv.x * 100.0;
    float u = luv.y * 200.0 - 100.0;
    float v = luv.z * 200.0 - 100.0;

    if (L < 0.0001) {
        return vec3(0.0);
    }

    // Reference white u', v'
    float denom_n = D65.x + 15.0 * D65.y + 3.0 * D65.z;
    float u_prime_n = (4.0 * D65.x) / denom_n;
    float v_prime_n = (9.0 * D65.y) / denom_n;

    float u_prime = u / (13.0 * L) + u_prime_n;
    float v_prime = v / (13.0 * L) + v_prime_n;

    float Y = L > 8.0 ? pow((L + 16.0) / 116.0, 3.0) : L / 903.3;
    Y *= D65.y;

    float X = (v_prime > 0.0001) ? Y * (9.0 * u_prime) / (4.0 * v_prime) : 0.0;
    float Z = (v_prime > 0.0001) ? Y * (12.0 - 3.0 * u_prime - 20.0 * v_prime) / (4.0 * v_prime) : 0.0;

    return xyz_to_rgb(vec3(X, Y, Z));
}

// ============================================================================
// RGB <-> HCL (Cylindrical LAB - Hue/Chroma/Luminance)
// ============================================================================

vec3 rgb_to_hcl(vec3 rgb) {
    vec3 lab = rgb_to_lab(rgb);
    // Denormalize lab for calculation
    float L = lab.x * 100.0;
    float a = lab.y * 255.0 - 128.0;
    float b = lab.z * 255.0 - 128.0;

    float C = sqrt(a * a + b * b);
    float H = atan(b, a);
    if (H < 0.0) H += 2.0 * PI;

    // Normalize to [0,1]
    return vec3(H / (2.0 * PI), C / 180.0, L / 100.0);
}

vec3 hcl_to_rgb(vec3 hcl) {
    float H = hcl.x * 2.0 * PI;
    float C = hcl.y * 180.0;
    float L = hcl.z * 100.0;

    float a = C * cos(H);
    float b = C * sin(H);

    // Normalize to [0,1] for lab_to_rgb
    vec3 lab = vec3(L / 100.0, (a + 128.0) / 255.0, (b + 128.0) / 255.0);
    return lab_to_rgb(lab);
}

// ============================================================================
// RGB <-> YCbCr (BT.601)
// ============================================================================

vec3 rgb_to_ycbcr(vec3 rgb) {
    float Y  =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
    float Cb = -0.169 * rgb.r - 0.331 * rgb.g + 0.500 * rgb.b + 0.5;
    float Cr =  0.500 * rgb.r - 0.419 * rgb.g - 0.081 * rgb.b + 0.5;
    return vec3(Y, Cb, Cr);
}

vec3 ycbcr_to_rgb(vec3 ycbcr) {
    float Y  = ycbcr.x;
    float Cb = ycbcr.y - 0.5;
    float Cr = ycbcr.z - 0.5;

    float r = Y + 1.402 * Cr;
    float g = Y - 0.344 * Cb - 0.714 * Cr;
    float b = Y + 1.772 * Cb;

    return clamp(vec3(r, g, b), 0.0, 1.0);
}

// ============================================================================
// RGB <-> YUV (Analog video)
// ============================================================================

vec3 rgb_to_yuv(vec3 rgb) {
    float Y =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
    float U = -0.147 * rgb.r - 0.289 * rgb.g + 0.436 * rgb.b + 0.5;
    float V =  0.615 * rgb.r - 0.515 * rgb.g - 0.100 * rgb.b + 0.5;
    return vec3(Y, U, V);
}

vec3 yuv_to_rgb(vec3 yuv) {
    float Y = yuv.x;
    float U = yuv.y - 0.5;
    float V = yuv.z - 0.5;

    float r = Y + 1.140 * V;
    float g = Y - 0.395 * U - 0.581 * V;
    float b = Y + 2.032 * U;

    return clamp(vec3(r, g, b), 0.0, 1.0);
}

// ============================================================================
// RGB <-> YPbPr (Component video - analog version of YCbCr)
// ============================================================================

vec3 rgb_to_ypbpr(vec3 rgb) {
    float Y  =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
    float Pb = -0.169 * rgb.r - 0.331 * rgb.g + 0.500 * rgb.b + 0.5;
    float Pr =  0.500 * rgb.r - 0.419 * rgb.g - 0.081 * rgb.b + 0.5;
    return vec3(Y, Pb, Pr);
}

vec3 ypbpr_to_rgb(vec3 ypbpr) {
    float Y  = ypbpr.x;
    float Pb = ypbpr.y - 0.5;
    float Pr = ypbpr.z - 0.5;

    float r = Y + 1.402 * Pr;
    float g = Y - 0.344 * Pb - 0.714 * Pr;
    float b = Y + 1.772 * Pb;

    return clamp(vec3(r, g, b), 0.0, 1.0);
}

// ============================================================================
// RGB <-> YDbDr (SECAM video standard)
// ============================================================================

vec3 rgb_to_ydbdr(vec3 rgb) {
    float Y  =  0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
    float Db = -0.450 * rgb.r - 0.883 * rgb.g + 1.333 * rgb.b;
    float Dr = -1.333 * rgb.r + 1.116 * rgb.g + 0.217 * rgb.b;
    // Normalize Db, Dr from [-1.333, 1.333] to [0, 1]
    return vec3(Y, (Db + 1.333) / 2.666, (Dr + 1.333) / 2.666);
}

vec3 ydbdr_to_rgb(vec3 ydbdr) {
    float Y  = ydbdr.x;
    float Db = ydbdr.y * 2.666 - 1.333;
    float Dr = ydbdr.z * 2.666 - 1.333;

    float r = Y + 0.000092 * Db - 0.525912 * Dr;
    float g = Y - 0.129132 * Db + 0.267899 * Dr;
    float b = Y + 0.664679 * Db - 0.000079 * Dr;

    return clamp(vec3(r, g, b), 0.0, 1.0);
}

// ============================================================================
// RGB <-> CMY (Subtractive color - print)
// ============================================================================

vec3 rgb_to_cmy(vec3 rgb) {
    return vec3(1.0 - rgb.r, 1.0 - rgb.g, 1.0 - rgb.b);
}

vec3 cmy_to_rgb(vec3 cmy) {
    return vec3(1.0 - cmy.x, 1.0 - cmy.y, 1.0 - cmy.z);
}

// ============================================================================
// RGB <-> HWB (Hue/Whiteness/Blackness - CSS standard)
// ============================================================================

vec3 rgb_to_hwb(vec3 rgb) {
    vec3 hsv = rgb_to_hsv(rgb);
    float W = min(min(rgb.r, rgb.g), rgb.b);
    float B = 1.0 - max(max(rgb.r, rgb.g), rgb.b);
    return vec3(hsv.x, W, B);
}

vec3 hwb_to_rgb(vec3 hwb) {
    float H = hwb.x;
    float W = hwb.y;
    float B = hwb.z;

    // Normalize if W + B >= 1
    if (W + B >= 1.0) {
        float scale = 1.0 / (W + B);
        W *= scale;
        B *= scale;
    }

    vec3 rgb = hsv_to_rgb(vec3(H, 1.0, 1.0));
    rgb = rgb * (1.0 - W - B) + W;
    return rgb;
}

// ============================================================================
// RGB <-> OHTA (Optimal color features - good for image analysis)
// ============================================================================

vec3 rgb_to_ohta(vec3 rgb) {
    float I1 = (rgb.r + rgb.g + rgb.b) / 3.0;
    float I2 = (rgb.r - rgb.b) / 2.0 + 0.5;
    float I3 = (2.0 * rgb.g - rgb.r - rgb.b) / 4.0 + 0.5;
    return vec3(I1, I2, I3);
}

vec3 ohta_to_rgb(vec3 ohta) {
    float I1 = ohta.x;
    float I2 = ohta.y - 0.5;
    float I3 = ohta.z - 0.5;

    float r = I1 + I2 - I3 * 2.0 / 3.0;
    float g = I1 + I3 * 4.0 / 3.0;
    float b = I1 - I2 - I3 * 2.0 / 3.0;

    return clamp(vec3(r, g, b), 0.0, 1.0);
}

// ============================================================================
// RGB <-> YXY (CIE chromaticity - xyY color space)
// ============================================================================

vec3 rgb_to_yxy(vec3 rgb) {
    vec3 xyz = rgb_to_xyz(rgb);
    float sum = xyz.x + xyz.y + xyz.z;

    if (sum < 0.0001) {
        // White point chromaticity for zero luminance
        return vec3(0.0, 0.3127, 0.3290);
    }

    float x = xyz.x / sum;
    float y_chrom = xyz.y / sum;
    float Y = xyz.y;  // Luminance

    return vec3(Y, x, y_chrom);
}

vec3 yxy_to_rgb(vec3 yxy) {
    float Y = yxy.x;
    float x = yxy.y;
    float y_chrom = yxy.z;

    if (y_chrom < 0.0001) {
        return vec3(0.0);
    }

    float X = (x * Y) / y_chrom;
    float Z = ((1.0 - x - y_chrom) * Y) / y_chrom;

    return xyz_to_rgb(vec3(X, Y, Z));
}

// ============================================================================
// RGB <-> GREY (Grayscale - luma only)
// ============================================================================

vec3 rgb_to_grey(vec3 rgb) {
    float Y = 0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b;
    return vec3(Y, Y, Y);
}

vec3 grey_to_rgb(vec3 grey) {
    // All channels should be the same, use first
    return vec3(grey.x, grey.x, grey.x);
}

// ============================================================================
// Conversion dispatcher
// ============================================================================

vec3 to_rgb(vec3 color, int space) {
    switch (space) {
        case CS_RGB:   return color;
        case CS_HSV:   return hsv_to_rgb(color);
        case CS_HSL:   return hsl_to_rgb(color);
        case CS_YCbCr: return ycbcr_to_rgb(color);
        case CS_YUV:   return yuv_to_rgb(color);
        case CS_LAB:   return lab_to_rgb(color);
        case CS_XYZ:   return xyz_to_rgb(color);
        case CS_LUV:   return luv_to_rgb(color);
        case CS_HCL:   return hcl_to_rgb(color);
        case CS_CMY:   return cmy_to_rgb(color);
        case CS_HWB:   return hwb_to_rgb(color);
        case CS_YPbPr: return ypbpr_to_rgb(color);
        case CS_YDbDr: return ydbdr_to_rgb(color);
        case CS_OHTA:  return ohta_to_rgb(color);
        case CS_YXY:   return yxy_to_rgb(color);
        case CS_GREY:  return grey_to_rgb(color);
        default:       return color;
    }
}

vec3 from_rgb(vec3 rgb, int space) {
    switch (space) {
        case CS_RGB:   return rgb;
        case CS_HSV:   return rgb_to_hsv(rgb);
        case CS_HSL:   return rgb_to_hsl(rgb);
        case CS_YCbCr: return rgb_to_ycbcr(rgb);
        case CS_YUV:   return rgb_to_yuv(rgb);
        case CS_LAB:   return rgb_to_lab(rgb);
        case CS_XYZ:   return rgb_to_xyz(rgb);
        case CS_LUV:   return rgb_to_luv(rgb);
        case CS_HCL:   return rgb_to_hcl(rgb);
        case CS_CMY:   return rgb_to_cmy(rgb);
        case CS_HWB:   return rgb_to_hwb(rgb);
        case CS_YPbPr: return rgb_to_ypbpr(rgb);
        case CS_YDbDr: return rgb_to_ydbdr(rgb);
        case CS_OHTA:  return rgb_to_ohta(rgb);
        case CS_YXY:   return rgb_to_yxy(rgb);
        case CS_GREY:  return rgb_to_grey(rgb);
        default:       return rgb;
    }
}

void main() {
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(input_image);

    // Bounds check
    if (pixel.x >= size.x || pixel.y >= size.y) {
        return;
    }

    // Load pixel
    vec4 color = imageLoad(input_image, pixel);

    // Convert: source -> RGB -> target
    vec3 rgb = to_rgb(color.rgb, from_space);
    vec3 result = from_rgb(rgb, to_space);

    imageStore(output_image, pixel, vec4(result, color.a));
}
