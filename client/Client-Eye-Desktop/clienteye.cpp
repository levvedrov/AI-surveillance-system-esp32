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
#include <QElapsedTimer>
#include <QDebug>

int IsIpAvailable(QString input_ip) {
    QString ip = input_ip;
    return ip.isEmpty() ? 0 : 1;
}

void ClientEye::fetchAliveCams() {
    const QUrl url(QString("http://%1:%2/getaliveips").arg(serverIp).arg(serverPort));
    QNetworkReply *reply = netManager->get(QNetworkRequest{url});

    connect(reply, &QNetworkReply::finished, this, [=]() {
        const QByteArray raw = reply->readAll();
        const QJsonArray cams = QJsonDocument::fromJson(raw).object()["cams"].toArray();

        QSet<QString> aliveNow;
        for (const QJsonValue &v : cams) {
            QString ip = v.toString();
            aliveNow.insert(ip);
            requestCameraFrame(ip);
        }

        for (auto it = camStatusIndicators.begin(); it != camStatusIndicators.end(); ++it) {
            QString ip = it.key();
            QLabel* status = it.value();

            if (!camLabels.contains(ip)) continue;

            if (aliveNow.contains(ip)) {
                status->setStyleSheet("background-color: #2ecc71; border-radius: 6px;");
            } else {
                status->setStyleSheet("background-color: #e74c3c; border-radius: 6px;");
            }
        }

        reply->deleteLater();
    });
}

void ClientEye::requestCameraFrame(const QString &rawCamIp) {
    auto normalizeIp = [](const QString& ip) {
        QUrl u(ip);
        return u.host().isEmpty() ? ip.trimmed() : u.host().trimmed();
    };

    QString camIp = normalizeIp(rawCamIp);

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
                camWidget->setStyleSheet(R"(
                    background-color: #2c2c2c;
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 6px;
                )");

                QVBoxLayout *layout = new QVBoxLayout(camWidget);
                layout->setContentsMargins(6, 6, 6, 6);
                layout->setSpacing(6);

                QLabel *statusLabel = new QLabel;
                statusLabel->setFixedSize(12, 12);
                statusLabel->setStyleSheet("background-color: gray; border-radius: 6px;");
                layout->addWidget(statusLabel, 0, Qt::AlignLeft);
                camStatusIndicators.insert(camIp, statusLabel);

                QLabel *imgLabel = new QLabel;
                imgLabel->setObjectName("imgLabel");
                QSize fixedSize(320, 240);
                imgLabel->setFixedSize(fixedSize);
                imgLabel->setAlignment(Qt::AlignCenter);
                imgLabel->setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;");
                imgLabel->setPixmap(px.scaled(fixedSize, Qt::KeepAspectRatio, Qt::SmoothTransformation));
                layout->addWidget(imgLabel);

                QLabel *ipLabel = new QLabel(camIp);
                ipLabel->setAlignment(Qt::AlignCenter);
                ipLabel->setStyleSheet("color: #bbbbbb; font-size: 10pt; font-weight: bold;");
                layout->addWidget(ipLabel);

                ui->camGrid->addWidget(camWidget, currentRow, currentCol);
                camLabels.insert(camIp, camWidget);
                camErrorCount[camIp] = 0;

                if (++currentCol >= maxCols) {
                    currentCol = 0;
                    ++currentRow;
                }
            }
        } else {
            camErrorCount[camIp]++;
        }

        rep->deleteLater();
    });
}

void ClientEye::updateServerStatus() {
    QString serverUrl = QString("http://%1:%2/ping").arg(serverIp).arg(serverPort);
    QElapsedTimer timer;
    timer.start();

    QNetworkRequest request((QUrl(serverUrl)));
    QNetworkReply* reply = netManager->get(request);

    connect(reply, &QNetworkReply::finished, this, [=]() {
        bool online = reply->error() == QNetworkReply::NoError;
        qint64 latency = timer.elapsed();

        if (online) {
            ui->serverStatusCircle->setStyleSheet(
                "background-color: #2ecc71; border-radius: 12px; color: white; font-weight: bold;"
                );
            ui->serverStatusCircle->setText(QString::number(latency));

            ui->ServerIpLable->setText(
                QString("Server http://%1:%2 is live").arg(serverIp).arg(serverPort)
                );
        } else {
            ui->serverStatusCircle->setStyleSheet(
                "background-color: #e74c3c; border-radius: 12px; color: white; font-weight: bold;"
                );
            ui->serverStatusCircle->setText("×");

            ui->ServerIpLable->setText(
                QString("Server http://%1:%2 is offline").arg(serverIp).arg(serverPort)
                );
        }

        reply->deleteLater();
    });
}

ClientEye::ClientEye(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::ClientEye)
{
    ui->setupUi(this);
    ui->camGrid->setAlignment(Qt::AlignTop | Qt::AlignLeft);
    ui->camGrid->setSpacing(15);
    ui->camGrid->setContentsMargins(20, 20, 20, 20);

    netManager = new QNetworkAccessManager(this);

    serverIp = "192.168.50.226";
    serverPort = 5000;

    ui->serverStatusCircle->setAlignment(Qt::AlignCenter);
    ui->serverStatusCircle->setFixedSize(24, 24);
    ui->serverStatusCircle->setStyleSheet("background-color: gray; border-radius: 12px; color: white;");

    // Start camera fetcher
    QTimer* camTimer = new QTimer(this);
    connect(camTimer, &QTimer::timeout, this, [=]() {
        fetchAliveCams();
    });
    camTimer->start(100);

    // Start server status updater
    QTimer* statusTimer = new QTimer(this);
    connect(statusTimer, &QTimer::timeout, this, [=]() {
        updateServerStatus();
    });
    statusTimer->start(100);

    updateServerStatus(); // Initial check
}

ClientEye::~ClientEye() {
    delete ui;
}
