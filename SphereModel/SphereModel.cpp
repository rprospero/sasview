#include "ModelInfo.h"

#define M_PI 3.14159265358979323846

ParameterInfo param_infos[] = {
    // name         description            units    default        min     max    flags 
    { "scale"     , "I"                  , ""     ,    1.0,        0.0, +DBL_INF, PF_None},
    { "radius"    , "radius of sphere"   , "A"    ,   20.0,        0.0, +DBL_INF, PF_Polydisperse},
    { "sldSph"    , "sphere SLD"         , "1/A^2", 4.0e-6,   -10.0e-6,  20.0e-6, PF_None},
    { "sldSolv"   , "solvent SLD"        , "1/A^2", 4.0e-6,   -10.0e-6,  20.0e-6, PF_None},
    { "background", "constant background", "1/cm" ,    0.0,        0.0, +DBL_INF, PF_None},
};

ModelInfo model_info(
    "Sphere",
    "P(q)= analytic spere + bkg",
    GetParameterCount(param_infos),
    param_infos);

// model handling
CExport void* get_model_info() {
    return &model_info;
}


// Modified from sphere form calculator from libigor
// scale and bkg moved to caller
double SphereForm(double radius, double delrho, double q) {
    double bes, f, vol, f2, qr;

    //handle qr==0 separately
    qr = q * radius;
    if(qr == 0.0)
        bes = 1.0;
    else
        bes = 3.0*(sin(qr)-qr*cos(qr))/(qr*qr*qr);
        
    vol = 4.0*M_PI/3.0*radius*radius*radius;
    f   = vol*bes*delrho;       // [=] A-1

    // normalize to single particle volume, convert to 1/cm
    f2 = f * f / vol * 1.0e8;   // [=] 1/cm
        
    return f2;
}

// calculations
CExport void calculate_q(void* ptr, void** p, size_t nq, double iq[], double q[]) {
    if ((p == NULL) || (*p == NULL))
        return;

    const double scale      = AsSimpleParameter(p[0]);
    const double background = AsSimpleParameter(p[4]);
    const double delRho     = AsSimpleParameter(p[2]) - AsSimpleParameter(p[3]);
    
    // Get the dispersion points for the radius
    const PolydisperseParameter& radius = AsPolydisperseParameter(p[1]);

    // Perform the computation, with all weight points
    double sum  = 0.0;
    double norm = 0.0;
    double vol  = 0.0;

    // Loop over radius weight points
    for (size_t i = 0; i < nq; i++) {
        const double qi = q[i];

        for(size_t ri = 0; ri< radius.Length; ri++) {
            const double& r = radius.Values[ri];
            const double& w = radius.Weights[ri];

            //Un-normalize SphereForm by volume
            sum += w * SphereForm(r, delRho, qi) * (r * r * r);

            //Find average volume
            vol  += w  * (r * r * r);
            norm += w;
        }

        //Re-normalize by avg volume
        if ((vol != 0.0) && (norm != 0.0))
            sum /= (vol / norm);

        iq[i] = scale * sum / norm + background;
    }
}
CExport double calculate_ER(void* ptr, void** p) {
    if ((p == NULL) || (*p == NULL))
        return DBL_NAN;

    // Perform the computation, with all weight points
    double sum  = 0.0;
    double norm = 0.0;

    // Get the dispersion points for the radius
    const PolydisperseParameter& radius = AsPolydisperseParameter(p[1]);

    // Loop over radius weight points to average the radius value
    for (size_t ri = 0; ri < radius.Length; ri++) {
        const double& r = radius.Values[ri];
        const double& w = radius.Weights[ri];

        sum  += w * r;
        norm += w;
    }

    if (norm != 0)
        return sum / norm; //return the averaged value
    else
        return sum;
}
CExport double calculate_VR(void* ptr, void** p) {
    if ((p == NULL) || (*p == NULL))
        return DBL_NAN;

    return 1.0;
}
