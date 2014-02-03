#ifndef CUSTOMHEADER_H
#define CUSTOMHEADER_H

#include <QWidget>

class QPushButton;
class CustomHeader : public QWidget
{
Q_OBJECT
public:
    explicit CustomHeader(QWidget *parent = 0);
    void addSection(const QString &txt);
    int count() const { return m_sections.size(); }

signals:

public slots:
private:
    QList<QPushButton*> m_sections;
};

#endif // CUSTOMHEADER_H
