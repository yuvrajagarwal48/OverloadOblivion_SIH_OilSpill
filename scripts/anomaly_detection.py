import os
import pandas as pd
import pickle
import numpy as np
import torch
import torch.nn as nn
import warnings

warnings.filterwarnings("ignore")


class BiLSTM(nn.Module):
    def __init__(
        self,
        input_size=7,
        hidden_size=128,
        output_size=1,
        num_layers=2,
        dropout_rate=0.2,
    ):
        super(BiLSTM, self).__init__()  # Use super() for proper initialization
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
        )
        self.batch_norm = nn.BatchNorm1d(hidden_size * 2)  # Bidirectional output size
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(hidden_size * 2, 1)

    def forward(self, x):
        # LSTM forward pass
        out, _ = self.lstm(x)  # (batch_size, seq_length, hidden_size * 2)
        out = out[:, -1, :]  # (batch_size, hidden_size * 2)
        out = self.dropout(out)
        out = self.fc(out)
        return out.squeeze()  # Ensure output is 1D


class AnomalyDetector:
    def __init__(self, model_folder="models/lstm_model_7"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_folder = model_folder
        # Load the models and scaler
        self.scaler = self.load_scaler()
        self.label_encoder = self.load_encoder()
        self.model = self.load_model()

    def load_scaler(self):
        with open(os.path.join(self.model_folder, "scaler.pkl"), "rb") as f:
            return pickle.load(f)

    def load_encoder(self):
        with open(os.path.join(self.model_folder, "label_encoder.pkl"), "rb") as f:
            return pickle.load(f)

    def load_model(self):
        # Determine the device
        # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Create model
        model = BiLSTM()

        # Load model to the appropriate device
        model.load_state_dict(
            torch.load(
                os.path.join(self.model_folder, "best_model.pth"),
                map_location=self.device,
            )
        )

        # Move model to the device
        model = model.to(self.device)
        model.eval()

        return model

    def prepare_data(self, df):
        df["TimeOfDay_mode"] = self.label_encoder.transform(df["TimeOfDay_mode"])
        continuous_features = [
            "SOG_mean",
            "COG_mean",
            "LAT_mean",
            "LON_mean",
            "Heading_mean_heading",
        ]
        df[continuous_features] = self.scaler.transform(df[continuous_features])[0]
        # print(df)
        return df

    def predict(self, input_data):
        # Preprocess input data
        input_tensor = (
            torch.FloatTensor(np.array(input_data, dtype=float))
            .unsqueeze(0)
            .to(self.device)
        )  # Add batch dimension

        with torch.no_grad():
            outputs = self.model(input_tensor)

        predicted_value = torch.sigmoid(outputs).cpu().numpy()
        return predicted_value

    def detect_anomaly(self, input_data):
        input_df = input_data.to_frame().T
        input = self.prepare_data(input_df)
        predicted_value = self.predict(input)
        return {
            "anomaly": predicted_value > 0.32,
            "anomaly_probability": predicted_value,
        }


# df=pd.read_csv("/home/yuvraj/Coding/sih/data/trial_data.csv")
# # df.drop(['MMSI','TimeWindow','VesselType_mode','Cargo_mode'],axis=1,inplace=True)
# df=pd.read_csv("/home/yuvraj/Coding/sih/data/april_2015_anomaly_final.csv",on_bad_lines='skip')
# df.drop(['MMSI','TimeWindow','TimeOfDay','anomaly','VesselType_mode','Cargo_mode'],axis=1,inplace=True)
# anomaly_detector=AnomalyDetector()


# an=[515,
#  516,
#  517,
#  518,
#  520,
#  523,
#  524,
#  525,
#  526,
#  527,
#  528,
#  529,
#  530,
#  531,
#  532,
#  533,
#  534,
#  535,
#  536,
#  537,
#  538,
#  539,
#  540,
#  541,
#  542,
#  543,
#  544,
#  545,
#  546,
#  547,
#  548,
#  549,
#  550,
#  551,
#  553,
#  554,
#  555,
#  556,
#  2016,
#  3563,
#  3564,
#  3673,
#  4687,
#  4688,
#  4689,
#  4810,
#  4811,
#  4812,
#  4813,
#  4814,
#  4815,
#  4816,
#  4817,
#  4818,
#  4819,
#  4820,
#  4821,
#  4823,
#  4824,
#  4825,
#  4827,
#  4828,
#  4829,
#  4830,
#  4831,
#  4832,
#  4833,
#  4948,
#  4949,
#  4950,
#  4951,
#  4952,
#  4953,
#  4954,
#  5380,
#  5381,
#  5383,
#  5384,
#  5385,
#  5386,
#  5387,
#  5391,
#  5392,
#  5393,
#  5394,
#  5395,
#  5396,
#  5397,
#  5398,
#  5472,
#  5474,
#  5475,
#  5476,
#  5477,
#  5478,
#  5479,
#  6063,
#  6065,
#  6066,
#  6067,
#  6068,
#  6069,
#  6734,
#  6735,
#  7881,
#  7882,
#  8319,
#  8320,
#  8321,
#  9064,
#  9065,
#  9715,
#  9716,
#  9717,
#  9718,
#  9719,
#  9720,
#  9721,
#  9831,
#  10479,
#  10480,
#  10484,
#  12245,
#  12246,
#  12247,
#  12248,
#  12249,
#  12250,
#  12251,
#  12252,
#  12253,
#  12254,
#  12255,
#  12256,
#  12257,
#  12258,
#  12259,
#  12260,
#  12261,
#  12262,
#  12263,
#  12264,
#  12265,
#  12266,
#  12267,
#  12268,
#  12269,
#  12270,
#  12271,
#  12272,
#  12273,
#  12274,
#  12275,
#  12276,
#  12277,
#  12278,
#  12279,
#  12280,
#  12281,
#  12282,
#  12283,
#  12284,
#  12285,
#  12286,
#  12287,
#  12288,
#  12289,
#  12290,
#  12291,
#  12292,
#  12293,
#  12294,
#  12295,
#  12296,
#  12297,
#  12298,
#  12299,
#  12300,
#  12301,
#  12302,
#  12303,
#  12304,
#  12305,
#  12306,
#  12307,
#  12308,
#  12309,
#  12310,
#  12311,
#  12312,
#  12313,
#  12314,
#  12315,
#  12316,
#  14493,
#  18005,
#  18006,
#  18007,
#  18008,
#  18033,
#  18034,
#  18035,
#  18044,
#  18046,
#  18047,
#  18048,
#  18124,
#  18125,
#  18126,
#  18127,
#  18128,
#  18129,
#  18130,
#  18131,
#  18132,
#  18133,
#  18134,
#  18135,
#  18137,
#  18138,
#  18139,
#  18140,
#  18141,
#  18215,
#  18216,
#  18217,
#  18220,
#  18221,
#  18225,
#  18226,
#  18227,
#  18228,
#  18229,
#  18230,
#  18231,
#  18232,
#  18233,
#  18234,
#  18235,
#  18237,
#  18238,
#  18239,
#  18241,
#  18244,
#  18247,
#  18248,
#  18249,
#  18250,
#  18251,
#  18253,
#  18256,
#  18257,
#  18258,
#  18259,
#  18260,
#  18422,
#  18423,
#  18424,
#  18425,
#  18426,
#  18428,
#  18429,
#  19830,
#  19831,
#  19833,
#  19834,
#  19888,
#  19889,
#  19890,
#  19891,
#  19892,
#  20886,
#  20887,
#  20888,
#  20889,
#  20890,
#  20891,
#  20892,
#  20893,
#  20894,
#  20895,
#  20896,
#  20897,
#  20898,
#  20899,
#  20900,
#  20901,
#  20902,
#  20903,
#  20904,
#  20905,
#  20906,
#  20907,
#  20908,
#  20909,
#  20918,
#  20919,
#  20920,
#  20921,
#  20922,
#  20923,
#  20924,
#  20925,
#  20926,
#  20927,
#  20928,
#  20929,
#  20936,
#  20937,
#  20938,
#  20939,
#  20940,
#  20941,
#  20942,
#  20943,
#  20944,
#  20945,
#  20946,
#  20947,
#  20948,
#  20953,
#  23179,
#  23191,
#  23217,
#  23218,
#  23226,
#  23227,
#  23228,
#  23246,
#  24168,
#  24173,
#  24178,
#  24179,
#  24180,
#  24182,
#  24183,
#  24185,
#  24188,
#  24189,
#  24190,
#  25996,
#  25997,
#  26996,
#  27000,
#  27004,
#  27005,
#  27006,
#  27007,
#  27009,
#  27010,
#  27013,
#  28841,
#  28842,
#  28843,
#  28850,
#  28851,
#  28852,
#  28853,
#  28855,
#  28858,
#  28860,
#  28861,
#  28862,
#  28867,
#  28868,
#  28869,
#  28870,
#  28871,
#  28872,
#  28873,
#  28874,
#  28875,
#  30662,
#  30664,
#  30665,
#  32726,
#  32727,
#  32850,
#  32851,
#  32858,
#  32925,
#  32926,
#  32927,
#  32928,
#  32929,
#  32954,
#  32955,
#  32956,
#  32957,
#  32958,
#  32959,
#  32960,
#  32961,
#  32962,
#  32963,
#  32964,
#  32965,
#  34275,
#  34276,
#  34277,
#  34278,
#  34279,
#  34282,
#  34284,
#  34285,
#  34286,
#  34568,
#  34572,
#  34902,
#  34903,
#  34904,
#  37918,
#  37919,
#  37920,
#  37921,
#  37922,
#  37923,
#  37924,
#  37925,
#  37926,
#  37927,
#  37928,
#  37929,
#  37930,
#  37931,
#  37932,
#  37933,
#  37934,
#  37935,
#  37936,
#  37937,
#  37938,
#  37939,
#  37940,
#  37941,
#  37942,
#  37943,
#  37944,
#  37945,
#  37946,
#  37947,
#  37948,
#  37949,
#  37950,
#  37951,
#  37952,
#  37953,
#  37954,
#  37955,
#  37956,
#  37957,
#  37958,
#  37959,
#  37960,
#  37961,
#  37962,
#  37963,
#  37964,
#  37965,
#  37966,
#  37967,
#  37968,
#  37969,
#  37970,
#  37971,
#  37972,
#  37973,
#  37974,
#  37975,
#  37976,
#  37977,
#  37978,
#  37979,
#  37980,
#  37981,
#  37982,
#  37983,
#  37984,
#  37985,
#  37986,
#  37987,
#  37988,
#  37989,
#  38363,
#  38420,
#  38422,
#  38423,
#  40375,
#  40376,
#  40377,
#  40388,
#  40389,
#  40390,
#  40391,
#  40392,
#  40393,
#  40394,
#  40395,
#  40396,
#  40397,
#  40398,
#  40399,
#  40400,
#  40401,
#  40402,
#  40403,
#  40404,
#  40405,
#  40406,
#  40407,
#  40408,
#  40409,
#  40410,
#  40411,
#  40412,
#  40413,
#  40414,
#  40415,
#  40416,
#  40417,
#  40418,
#  40424,
#  40425,
#  40426,
#  41026,
#  41907,
#  41932,
#  59819,
#  59820,
#  59828,
#  59829,
#  59830,
#  59833,
#  59834,
#  59835,
#  59837,
#  59847,
#  59848,
#  59849,
#  59850,
#  59851,
#  59853,
#  59854,
#  59858,
#  59859,
#  59860,
#  59861,
#  60068,
#  60071,
#  60073,
#  60076,
#  60078,
#  60079,
#  60080,
#  60081,
#  60082,
#  60083,
#  60084,
#  60085,
#  60086,
#  62767,
#  62768,
#  65420,
#  65421,
#  65422,
#  65423,
#  65424,
#  65425,
#  65426,
#  65504,
#  65506,
#  68561,
#  68562,
#  68563,
#  68564,
#  68565,
#  68566,
#  68569,
#  68570,
#  68571,
#  68572,
#  68573,
#  68574,
#  68575,
#  68576,
#  68577,
#  68578,
#  68579,
#  68588,
#  68589,
#  68590,
#  68591,
#  68596,
#  71241,
#  71257,
#  71258,
#  71259,
#  71260,
#  71261,
#  71263,
#  71265,
#  71266,
#  71267,
#  71268,
#  71269,
#  71270,
#  71271,
#  71272,
#  71273,
#  71274,
#  71275,
#  71276,
#  71277,
#  71278,
#  71279,
#  71283,
#  71284,
#  71285,
#  71286,
#  71287,
#  71288,
#  71289,
#  71290,
#  71291,
#  71292,
#  71293,
#  71296,
#  71297,
#  71298,
#  71299,
#  71300,
#  71301,
#  71302,
#  71303,
#  71304,
#  71307,
#  71308,
#  71309,
#  71310,
#  71311,
#  71352,
#  71353,
#  71354,
#  71355,
#  71356,
#  71357,
#  71358,
#  71359,
#  71360,
#  71361,
#  71362,
#  71363,
#  71364,
#  71365,
#  71366,
#  71367,
#  71368,
#  72694,
#  72695,
#  72696,
#  72697,
#  72698,
#  72699,
#  72700,
#  72701,
#  72702,
#  72703,
#  72704,
#  72705,
#  73012,
#  73047,
#  73048,
#  73067,
#  73070,
#  73072,
#  73073,
#  73075,
#  73076,
#  73077,
#  73078,
#  73079,
#  73080,
#  73081,
#  73479,
#  73480,
#  73726,
#  73727,
#  73983,
#  73984,
#  73985,
#  73986,
#  73987,
#  73988,
#  73989,
#  73990,
#  73991,
#  73992,
#  73993,
#  73994,
#  73995,
#  73996,
#  73997,
#  73998,
#  73999,
#  74000,
#  74001,
#  74002,
#  74003,
#  74004,
#  74005,
#  74006,
#  74007,
#  74008,
#  74009,
#  74010,
#  74011,
#  74012,
#  74732,
#  74733,
#  74734,
#  74735,
#  74736,
#  74737,
#  74738,
#  74739,
#  74740,
#  74741,
#  74742,
#  74743,
#  74744,
#  74745,
#  74746,
#  74747,
#  74748,
#  74749,
#  74750,
#  74751,
#  74752,
#  74753,
#  74754,
#  74755,
#  74756,
#  74757,
#  74758,
#  74759,
#  74760,
#  74761,
#  74762,
#  74763,
#  74764,
#  74765,
#  74766,
#  74767,
#  74768,
#  74769,
#  74770,
#  74771,
#  74772,
#  74773,
#  74774,
#  74775,
#  74776,
#  74777,
#  74778,
#  74779,
#  74780,
#  74781,
#  74782,
#  74783,
#  74784,
#  74785,
#  74786,
#  74787,
#  74788,
#  74789,
#  74790,
#  74791,
#  74792,
#  74793,
#  74794,
#  74795,
#  74796,
#  74797,
#  74798,
#  74799,
#  74800,
#  74801,
#  74802,
#  74803,
#  75518,
#  75519,
#  75520,
#  75521,
#  76422,
#  76423,
#  76514,
#  76515,
#  76516,
#  76517,
#  76518,
#  76519,
#  76520,
#  76521,
#  76522,
#  76523,
#  76524,
#  76525,
#  76526,
#  76527,
#  76528,
#  76529,
#  76530,
#  76531,
#  76532,
#  76533,
#  76534,
#  76535,
#  76536,
#  76537,
#  76538,
#  76539,
#  76540,
#  76541,
#  76542,
#  76543,
#  76544,
#  76545,
#  76546,
#  76547,
#  76548,
#  76549,
#  76550,
#  76551,
#  76552,
#  76553,
#  76554,
#  76555,
#  76556,
#  77920,
#  77921,
#  77922,
#  77923,
#  77924,
#  77925,
#  77926,
#  77927,
#  77928,
#  77929,
#  77930,
#  77931,
#  77932,
#  77933,
#  77934,
#  77935,
#  77936,
#  77937,
#  77938,
#  77939,
#  77940,
#  77941,
#  77942,
#  77960,
#  77961,
#  79498,
#  79499,
#  81542,
#  81543,
#  81560,
#  81573,
#  81575,
#  81576,
#  81577,
#  81578,
#  81579,
#  81580,
#  81581,
#  81582,
#  81583,
#  81757,
#  81758,
#  81759,
#  81760,
#  81761,
#  81762,
#  81763,
#  81764,
#  81765,
#  81766,
#  81767,
#  81806,
#  81807,
#  81808,
#  82595,
#  83694,
#  83695,
#  83696,
#  83697,
#  83698,
#  83699,
#  83702,
#  83703,
#  83721,
#  83723,
#  83973,
#  83975,
#  83992,
#  83994,
#  83995,
#  83997,
#  83998,
#  84000,
#  84002,
#  86601,
#  86610,
#  86611,
#  89696,
#  89697,
#  89700,
#  89703,
#  89704,
#  89707,
#  89717,
#  89718,
#  89722,
#  93577,
#  93578,
#  93579,
#  93580,
#  93581,
#  93582,
#  93583,
#  93584,
#  93585,
#  93586,
#  93587,
#  93588,
#  93589,
#  93590,
#  93591,
#  93592,
#  93593,
#  93594,
#  93595,
#  93596,
#  93597,
#  93598,
#  93599,
#  93600,
#  93601,
#  93602,
#  93603,
#  93604,
#  93605,
#  93606,
#  93607,
#  93608,
#  93609,
#  93610,
#  93611,
#  93612,
#  93631,
#  93632,
#  93633,
#  93634,
#  93635,
#  93636,
#  93639,
#  93640,
#  93641,
#  95752,
#  96614,
#  96615,
#  96616,
#  96617,
#  96618,
#  96619,
#  96620,
#  96621,
#  96781,
#  96782,
#  96783,
#  96784,
#  96785,
#  96786,
#  96787,
#  96788,
#  96789,
#  96790,
#  96791,
#  96792,
#  96793,
#  96794,
#  96795,
#  96796,
#  96797,
#  96798,
#  96799,
#  96800,
#  96801,
#  96802,
# ]
# for i in an:
#     print(anomaly_detector.detect_anomaly(df.loc[i]))
