#ifndef CLIENTEYE_H
#define CLIENTEYE_H

#include <QMainWindow>
#include <QPixmap>
#include <QString>
#include <QNetworkAccessManager>
#include <QHash>
#include <QLabel>

QT_BEGIN_NAMESPACE
namespace Ui {
class ClientEye;
}
QT_END_NAMESPACE

class ClientEye : public QMainWindow
{
    Q_OBJECT

public:
    explicit ClientEye(QWidget *parent = nullptr);
    ~ClientEye();

private:
    Ui::ClientEye *ui;
    QNetworkAccessManager* netManager;

    QString serverIp;
    int serverPort;
    void fetchAliveCams();

    QHash<QString, QWidget*> camLabels;

    int currentRow = 0;
    int currentCol = 0;
    const int maxCols = 3;
    QMap<QString, int> camErrorCount;                  // IP -> количество ошибок
    QMap<QString, QLabel*> camStatusIndicators;       // IP -> индикатор (цветная точка)


    void addFrame(const QPixmap& pixmap);
    void requestCameraFrame(const QString& camIp);
};

#endif // CLIENTEYE_H
