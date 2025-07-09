#include "clienteye.h"
#include "./ui_clienteye.h"
#include <QLabel>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QTimer>
#include <QPixmap>
#include <QImage>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QVBoxLayout>



int IsIpAvailable(QString input_ip){
    QString ip = input_ip;
    if (ip.isEmpty()){ return 0; }
    else{ return 1; }
}



void ClientEye::fetchAliveCams()
{
    auto normalizeIp = [](const QString& ip) {
        QUrl u(ip);
        return u.host().isEmpty() ? ip.trimmed() : u.host().trimmed();
    };

    const QUrl url(QString("http://%1:%2/getaliveips")
                       .arg(serverIp).arg(serverPort));

    QNetworkReply *reply = netManager->get(QNetworkRequest{url});

    connect(reply, &QNetworkReply::finished, this, [=]() {
        const QByteArray raw = reply->readAll();
        const QJsonArray cams =
            QJsonDocument::fromJson(raw).object()["cams"].toArray();

        QSet<QString> aliveNow;
        for (const QJsonValue &v : cams) {
            QString ip = v.toString();
            aliveNow.insert(ip);
            requestCameraFrame(ip);
        }

        // Обновление цветового индикатора каждой камеры
        for (auto it = camStatusIndicators.begin(); it != camStatusIndicators.end(); ++it) {
            QString ip = it.key();
            QLabel* status = it.value();

            if (!camLabels.contains(ip)) continue; // не вставлять цвет, если камеры нет

            if (aliveNow.contains(ip)) {
                status->setStyleSheet("background-color: #2ecc71; border-radius: 5px;");
            } else {
                status->setStyleSheet("background-color: #e74c3c; border-radius: 5px;");
            }
        }

        reply->deleteLater();
    });
}

void ClientEye::requestCameraFrame(const QString &rawCamIp)
{
    auto normalizeIp = [](const QString& ip) {
        QUrl u(ip);
        return u.host().isEmpty() ? ip.trimmed() : u.host().trimmed();
    };

    QString camIp = normalizeIp(rawCamIp); // 👈 нормализуем

    const QUrl url(QString("http://%1:%2/get?ip=%3")
                       .arg(serverIp).arg(serverPort).arg(camIp));

    QNetworkReply *rep = netManager->get(QNetworkRequest{url});

    connect(rep, &QNetworkReply::finished, this, [=]() {
        QByteArray data = rep->readAll();
        QPixmap px;
        bool netError = rep->error() != QNetworkReply::NoError;
        bool validImage = px.loadFromData(data);
        bool imageTooSmall = px.isNull() || px.width() < 20 || px.height() < 20;

        if (!netError && validImage && !imageTooSmall) {
            camErrorCount[camIp] = 0;

            if (camLabels.contains(camIp)) {
                QWidget* camBox = camLabels[camIp];
                QLabel* imgLabel = camBox->findChild<QLabel*>("imgLabel");
                if (imgLabel)
                    imgLabel->setPixmap(px.scaled(imgLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation));

            } else {
                QWidget *camWidget = new QWidget;
                camWidget->setStyleSheet("background-color: #1e1e1e; border: 1px solid #444; border-radius: 4px;");
                QVBoxLayout *layout = new QVBoxLayout(camWidget);
                layout->setContentsMargins(4, 4, 4, 4);
                layout->setSpacing(2);

                QLabel *statusLabel = new QLabel;
                statusLabel->setFixedSize(10, 10);
                statusLabel->setStyleSheet("background-color: gray; border-radius: 5px;");
                layout->addWidget(statusLabel, 0, Qt::AlignLeft);
                camStatusIndicators.insert(camIp, statusLabel);

                QLabel *imgLabel = new QLabel;
                imgLabel->setObjectName("imgLabel");
                QSize fixedSize(320, 240);
                imgLabel->setPixmap(px.scaled(fixedSize, Qt::KeepAspectRatio, Qt::SmoothTransformation));
                imgLabel->setFixedSize(fixedSize);
                imgLabel->setAlignment(Qt::AlignCenter);

                QLabel *ipLabel = new QLabel(camIp);
                ipLabel->setAlignment(Qt::AlignCenter);
                ipLabel->setStyleSheet("color: gray; font-size: 10pt;");

                layout->addWidget(imgLabel);
                layout->addWidget(ipLabel);

                ui->camGrid->addWidget(camWidget, currentRow, currentCol);
                camLabels.insert(camIp, camWidget);
                camErrorCount[camIp] = 0;

                if (++currentCol >= maxCols) { currentCol = 0; ++currentRow; }
            }

        } else {
            camErrorCount[camIp]++;
        }

        rep->deleteLater();
    });
}



ClientEye::ClientEye(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::ClientEye)
{
    ui->setupUi(this);
    ui->camGrid->setAlignment(Qt::AlignTop | Qt::AlignLeft);
    ui->camGrid->setSpacing(10);
    ui->camGrid->setContentsMargins(10, 10, 10, 10);
    // Инициализация netManager
    netManager = new QNetworkAccessManager(this);

    serverIp = "192.168.50.226";
    serverPort = 5000;
    QString serverUrl = QString("http://%1:%2").arg(serverIp).arg(serverPort);

    int status = IsIpAvailable(serverUrl);
    QString msg = "Null";

    switch(status){
    case 0:
        msg = "The IP is empty";
        break;
    case 1:
        msg = serverUrl + " is live.";
        break;
    }
    ui->ServerIpLable->setText(msg);

    QTimer* timer = new QTimer(this);
    connect(timer, &QTimer::timeout, this, [=]() {
        fetchAliveCams();  // теперь будет работать
    });
    timer->start(100);
}



ClientEye::~ClientEye()
{
    delete ui;
}
