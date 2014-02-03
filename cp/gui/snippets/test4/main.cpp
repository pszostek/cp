#include <QApplication>
#include <QTreeView>
#include <QHeaderView>
#include <QDirModel>
#include "customheader.h"

class TreeView : public QTreeView {
public:
    TreeView(QWidget *parent = 0) : QTreeView(parent){
        header()->hide();
        m_header = new CustomHeader(this);
        m_header->addSection("section 1");
        m_header->addSection("section 2");
        m_header->addSection("section 3");
    }
protected:
    void resizeEvent(QResizeEvent *event) {
        setViewportMargins(0, m_header->sizeHint().height(), 0, 0);
        m_header->setGeometry(0, 0, viewport()->width(), m_header->sizeHint().height());
    }
    void showEvent(QShowEvent *) {
        setViewportMargins(0, m_header->sizeHint().height(), 0, 0);
        m_header->setGeometry(0, 0, viewport()->width(), m_header->sizeHint().height());
    }

private:
    CustomHeader *m_header;
};

int main(int argc, char **argv){
    QApplication app(argc,argv);
    TreeView tv;
    QDirModel model;
    tv.setModel(&model);
    tv.setRootIndex(model.index("/"));
    tv.show();
    return app.exec();
}
