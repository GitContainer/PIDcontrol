#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QtWidgets>

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent=NULL);

private slots:
    void open();
    void save();

private:
    void createActions();
    void createMenu();

    QAction *openAct, *saveAct;
};

#endif // MAINWINDOW_H
